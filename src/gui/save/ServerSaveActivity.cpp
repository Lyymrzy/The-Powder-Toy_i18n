#include "ServerSaveActivity.h"
#include "graphics/Graphics.h"
#include "graphics/VideoBuffer.h"
#include "gui/interface/Label.h"
#include "gui/interface/Textbox.h"
#include "gui/interface/Button.h"
#include "gui/interface/Checkbox.h"
#include "gui/dialogues/ErrorMessage.h"
#include "gui/dialogues/SaveIDMessage.h"
#include "gui/dialogues/ConfirmPrompt.h"
#include "gui/dialogues/InformationMessage.h"
#include "client/Client.h"
#include "client/ThumbnailRendererTask.h"
#include "client/GameSave.h"
#include "client/http/UploadSaveRequest.h"
#include "tasks/Task.h"
#include "gui/Style.h"

class SaveUploadTask: public Task
{
	SaveInfo &save;

	void before() override
	{

	}

	void after() override
	{

	}

	bool doWork() override
	{
		notifyProgress(-1);
		auto uploadSaveRequest = std::make_unique<http::UploadSaveRequest>(save);
		uploadSaveRequest->Start();
		uploadSaveRequest->Wait();
		try
		{
			save.SetID(uploadSaveRequest->Finish());
		}
		catch (const http::RequestError &ex)
		{
			notifyError(ByteString(ex.what()).FromUtf8());
			return false;
		}
		return true;
	}

public:
	SaveUploadTask(SaveInfo &newSave):
		save(newSave)
	{

	}
};

ServerSaveActivity::ServerSaveActivity(std::unique_ptr<SaveInfo> newSave, OnUploaded onUploaded_) :
	WindowActivity(ui::Point(-1, -1), ui::Point(440, 200)),
	thumbnailRenderer(nullptr),
	save(std::move(newSave)),
	onUploaded(onUploaded_),
	saveUploadTask(nullptr)
{
	titleLabel = new ui::Label(ui::Point(4, 5), ui::Point((Size.X/2)-8, 16), "");
	titleLabel->SetTextColour(style::Colour::InformationTitle);
	titleLabel->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	titleLabel->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	AddComponent(titleLabel);
	CheckName(save->GetName()); //set titleLabel text

	ui::Label * previewLabel = new ui::Label(ui::Point((Size.X/2)+4, 5), ui::Point((Size.X/2)-8, 16), "预览：");
	previewLabel->SetTextColour(style::Colour::InformationTitle);
	previewLabel->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	previewLabel->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	AddComponent(previewLabel);

	nameField = new ui::Textbox(ui::Point(8, 25), ui::Point((Size.X/2)-16, 16), save->GetName(), "[存档名称]");
	nameField->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	nameField->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	nameField->SetActionCallback({ [this] { CheckName(nameField->GetText()); } });
	nameField->SetLimit(50);
	AddComponent(nameField);
	FocusComponent(nameField);

	descriptionField = new ui::Textbox(ui::Point(8, 65), ui::Point((Size.X/2)-16, Size.Y-(65+16+4)), save->GetDescription(), "[存档描述]");
	descriptionField->SetMultiline(true);
	descriptionField->SetLimit(254);
	descriptionField->Appearance.VerticalAlign = ui::Appearance::AlignTop;
	descriptionField->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	AddComponent(descriptionField);

	publishedCheckbox = new ui::Checkbox(ui::Point(8, 45), ui::Point((Size.X/2)-80, 16), "发布", "");
	auto user = Client::Ref().GetAuthUser();
	if (!(user && user->Username == save->GetUserName()))
	{
		//Save is not owned by the user, disable by default
		publishedCheckbox->SetChecked(false);
	}
	else
	{
		//Save belongs to the current user, use published state already set
		publishedCheckbox->SetChecked(save->GetPublished());
	}
	AddComponent(publishedCheckbox);

	pausedCheckbox = new ui::Checkbox(ui::Point(160, 45), ui::Point(55, 16), "已暂停", "");
	pausedCheckbox->SetChecked(save->GetGameSave()->paused);
	AddComponent(pausedCheckbox);

	ui::Button * cancelButton = new ui::Button(ui::Point(0, Size.Y-16), ui::Point((Size.X/2)-75, 16), "取消");
	cancelButton->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	cancelButton->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	cancelButton->Appearance.BorderInactive = ui::Colour(200, 200, 200);
	cancelButton->SetActionCallback({ [this] {
		Exit();
	} });
	AddComponent(cancelButton);
	SetCancelButton(cancelButton);

	ui::Button * okayButton = new ui::Button(ui::Point((Size.X/2)-76, Size.Y-16), ui::Point(76, 16), "保存");
	okayButton->Appearance.HorizontalAlign = ui::Appearance::AlignLeft;
	okayButton->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	okayButton->Appearance.TextInactive = style::Colour::InformationTitle;
	okayButton->SetActionCallback({ [this] {
		Save();
	} });
	AddComponent(okayButton);
	SetOkayButton(okayButton);

	ui::Button * PublishingInfoButton = new ui::Button(ui::Point((Size.X*3/4)-75, Size.Y-42), ui::Point(150, 16), "发布说明");
	PublishingInfoButton->Appearance.HorizontalAlign = ui::Appearance::AlignCentre;
	PublishingInfoButton->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	PublishingInfoButton->Appearance.TextInactive = style::Colour::InformationTitle;
	PublishingInfoButton->SetActionCallback({ [this] {
		ShowPublishingInfo();
	} });
	AddComponent(PublishingInfoButton);

	ui::Button * RulesButton = new ui::Button(ui::Point((Size.X*3/4)-75, Size.Y-22), ui::Point(150, 16), "上传规则");
	RulesButton->Appearance.HorizontalAlign = ui::Appearance::AlignCentre;
	RulesButton->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	RulesButton->Appearance.TextInactive = style::Colour::InformationTitle;
	RulesButton->SetActionCallback({ [this] {
		ShowRules();
	} });
	AddComponent(RulesButton);

	if (save->GetGameSave())
	{
		thumbnailRenderer = new ThumbnailRendererTask(*save->GetGameSave(), Size / 2 - Vec2(16, 16), RendererSettings::decorationAntiClickbait, true);
		thumbnailRenderer->Start();
	}
}

ServerSaveActivity::ServerSaveActivity(std::unique_ptr<SaveInfo> newSave, bool saveNow, OnUploaded onUploaded_) :
	WindowActivity(ui::Point(-1, -1), ui::Point(200, 50)),
	thumbnailRenderer(nullptr),
	save(std::move(newSave)),
	onUploaded(onUploaded_),
	saveUploadTask(nullptr)
{
	ui::Label * titleLabel = new ui::Label(ui::Point(0, 0), Size, "正在保存到服务器...");
	titleLabel->SetTextColour(style::Colour::InformationTitle);
	titleLabel->Appearance.HorizontalAlign = ui::Appearance::AlignCentre;
	titleLabel->Appearance.VerticalAlign = ui::Appearance::AlignMiddle;
	AddComponent(titleLabel);

	AddAuthorInfo();

	saveUploadTask = new SaveUploadTask(*this->save);
	saveUploadTask->AddTaskListener(this);
	saveUploadTask->Start();
}

void ServerSaveActivity::NotifyDone(Task * task)
{
	if(!task->GetSuccess())
	{
		Exit();
		new ErrorMessage("错误", task->GetError());
	}
	else
	{
		if (onUploaded)
		{
			onUploaded(std::move(save));
		}
		Exit();
	}
}

void ServerSaveActivity::Save()
{
	if (!nameField->GetText().length())
	{
		new ErrorMessage("错误", "你必须指定存档名称。");
		return;
	}
	// 官方服务器不支持非 ASCII 存档名，这里提前拦截并提示（与原始版本保持一致）
	bool asciiName = true;
	for (auto ch : nameField->GetText())
	{
		if (ch > 0x7F)
		{
			asciiName = false;
			break;
		}
	}
	if (!asciiName)
	{
		new ErrorMessage("名称无效", "在线存档名只能使用英文、数字与常见符号，不支持中文等非 ASCII 字符。\n请修改名称后再上传。");
		return;
	}
	auto user = Client::Ref().GetAuthUser();
	if (!(user && user->Username == save->GetUserName()) && publishedCheckbox->GetChecked())
	{
		new ConfirmPrompt("发布", "该存档由 " + save->GetUserName().FromUtf8() + " 创建，你即将以自己的名义发布它；如果你未获得作者许可，请取消勾选「发布」，否则可以继续", { [this] {
			saveUpload();
		} });
	}
	else
	{
		saveUpload();
	}
}

void ServerSaveActivity::AddAuthorInfo()
{
	Json::Value serverSaveInfo;
	serverSaveInfo["type"] = "save";
	serverSaveInfo["id"] = save->GetID();
	auto user = Client::Ref().GetAuthUser();
	serverSaveInfo["username"] = user ? user->Username : ByteString("");
	serverSaveInfo["title"] = save->GetName().ToUtf8();
	serverSaveInfo["description"] = save->GetDescription().ToUtf8();
	serverSaveInfo["published"] = (int)save->GetPublished();
	serverSaveInfo["date"] = (Json::Value::UInt64)time(nullptr);
	Client::Ref().SaveAuthorInfo(&serverSaveInfo);
	{
		auto gameSave = save->TakeGameSave();
		gameSave->authors = serverSaveInfo;
		save->SetGameSave(std::move(gameSave));
	}
}

void ServerSaveActivity::saveUpload()
{
	okayButton->Enabled = false;
	save->SetName(nameField->GetText());
	save->SetDescription(descriptionField->GetText());
	save->SetPublished(publishedCheckbox->GetChecked());
	auto user = Client::Ref().GetAuthUser();
	save->SetUserName(user ? user->Username : ByteString(""));
	save->SetID(0);
	{
		auto gameSave = save->TakeGameSave();
		gameSave->paused = pausedCheckbox->GetChecked();
		save->SetGameSave(std::move(gameSave));
	}
	AddAuthorInfo();
	uploadSaveRequest = std::make_unique<http::UploadSaveRequest>(*save);
	uploadSaveRequest->Start();
}

void ServerSaveActivity::Exit()
{
	WindowActivity::Exit();
}

void ServerSaveActivity::ShowPublishingInfo()
{
	String info =
		"在 The Powder Toy 中，你可以用两种隐私级别把模拟保存到自己的账号：已发布与未发布。勾选或取消勾选「发布」复选框即可切换。存档默认是未发布的，所以如果不勾选发布，就没有人能看见你的存档。\n"
		"\n"
		"\bt已发布的存档\bw 会出现在「按日期」列表中，被很多人看到；它们也会计入你的平均分，平均分会公开展示在网站的个人主页上。想让别人评论与投票的存档，就发布它。\n"
		"\bt未发布的存档\bw 不会出现在「按日期」列表中，也不计入平均分。不过它们并非完全私密：任何知道存档 ID 的人都能查看。你可以把 ID 发给特定的人，而不让所有人看到。\n"
		"\n"
		"想快速重新保存，打开存档后点击分体式重存按钮的左半边「重新上传当前模拟」。若要修改描述或发布状态，点击右半边「修改模拟属性」。注意：存档名称无法修改，改名会创建一个全新的存档（没有评论、投票与标签），与原存档无关。\n"
		"你可能想在存档完成后发布它，或把已发布的存档改为未发布。打开存档、点击「修改模拟属性」，在那里更改发布状态即可。也可以在浏览器的「我的」分类中选中若干存档，然后点击底部出现的按钮来 \bt取消发布或删除\bw。\n"
		"若存档创建不到一周就快速走红，会被自动放到 \bt首页\bw。只有已发布的存档才有机会。管理员也可以手动把存档推上首页，但很少这么做；对于违规或他们认为不合适的存档，管理员也可以将其从首页撤下。\n"
		"存档创建后可以随意重新保存，系统会保留一小段 \bt历史版本\bw。在存档浏览器中右键任意存档并选择「查看历史」即可查看，适合误存之后想回到旧版本的情况。\n"
		;

	new InformationMessage("发布说明", info, true);
}

void ServerSaveActivity::ShowRules()
{
	String rules =
		"\boS 部分：社交与社区规则\n"
		"\bw在与社区互动时，有几条规则需要遵守。这些规则由管理团队执行，任何违规问题都可能被其他用户反馈给我们。本部分适用于上传的存档、评论区、论坛以及社区的其它区域。\n"
		"\n"
		"\bt1. 尽量使用规范的语法。\bw 英语是官方社区语言，但在地区性或文化性群组中并不强制。如果你英语写得不好，建议使用翻译工具。\n"
		"\bt2. 请勿刷屏。\bw 这没有一刀切的定义，但其含义通常是明显的。此外，以下行为也视为刷屏，可能被隐藏或删除：\n"
		   "- 就同一主题发布多个帖子。关于游戏反馈或建议，请尽量合并到一个帖子中。\n"
		   "- 回复旧帖把它顶上来，即所谓「挖坟」。旧帖内容可能已经过时（已修复的问题、旧想法等）。建议为更新或当前的情况发新帖。\n"
		   "- 用「+1」之类的短回复顶帖。没必要反复顶帖而让别人难以找到回复。回复请留给有建设性的意见，想表达支持请使用「+1」按钮。\n"
		   "- 过长或毫无意义的评论。例如反复敲同一个字母，或几乎没有目的的评论。使用其它语言的评论不受此限。\n"
		   "- 过度排版。适度使用大写、加粗与斜体没问题，但请不要整篇都这样。\n"
		"\bt3. 尽量少说脏话。\bw 含有脏话的评论或存档可能会被删除，其它语言中的脏话同样适用。\n"
		"\bt4. 请勿上传色情、冒犯性或其它不当内容。\bw\n"
		   "- 包括但不限于：性、毒品、种族主义、过度政治内容，以及任何冒犯或侮辱某一群体的内容。\n"
		   "- 用其它语言提及这些内容同样禁止，请勿尝试绕过本规则。\n"
		   "- 禁止发布违反本规则的网址或图片，包括个人资料中的链接或文字。\n"
		"\bt5. 请勿宣传与 The Powder Toy 无关的第三方游戏、网站或其它地方。\bw\n"
		   "- 本规则主要用于防止有人到处宣传自己的游戏与产品。\n"
		   "- 未经授权的非官方社区聚集地（例如 Discord）也在禁止之列。\n"
		"\bt6. 禁止钓鱼捣乱。\bw 与某些规则一样，这没有明确定义。反复捣乱的用户更容易被封禁，且封禁时间更长。\n"
		"\bt7. 请勿冒充他人。\bw 禁止注册与社区或其它在线社区中他人名字故意相似的账号。\n"
		"\bt8. 请勿就管理员的处理决定或问题发帖。\bw 如果你的账号被封或内容被删除而有异议，请通过站内消息联系管理员；除此之外请避免讨论管理操作。\n"
		"\bt9. 请勿越俎代庖地「管理」。\bw 决定权在管理员手中。用户不应以封禁或违规后果去威胁他人。若有疑问或发现问题，建议使用「举报」按钮或站内消息反馈。\n"
		"\bt10. 禁止为违法行为张目。\bw 具体适用哪国法律并不明确，但有一些常识性内容，包括但不限于：\n"
		   "- 盗版软件、音乐等\n"
		   "- 入侵或盗取账号\n"
		   "- 盗窃或诈骗\n"
		"\bt11. 请勿跟踪或骚扰任何用户。\bw 近年来这类问题以各种形式增多，通常包括：\n"
		   "- 人肉搜索用户，找出其住址或真实身份\n"
		   "- 在对方明确不想联系时仍不断发消息\n"
		   "- 集体给存档点踩\n"
		   "- 在他人的内容（存档、论坛帖子等）下发布粗鲁或无意义的评论\n"
		   "- 煽动一群用户「针对」某位用户\n"
		   "- 私人争吵或仇恨，例如在评论区争吵或制作仇恨性质的存档\n"
		   "- 对人群的歧视，例如基于宗教、民族等\n"
		"\n"
		"\boG 部分：游戏内规则\n"
		"\bw本部分规则针对游戏内的行为。虽然 S 部分同样适用于游戏内，但以下规则更专注于游戏内的社区互动。\n"
		"\bt1. 不要把他人的作品据为己有。\bw 这可能是直接重新上传他人存档，或大量套用他人的存档内容。允许创作衍生作品，但须合规使用：默认情况下，使用他人作品必须署名；除非作者明确声明了其它使用条款，这就是标准政策。衍生作品的界定看创新程度与原创比例（即有多少原创、多少来自他人）。盗用他人存档会被取消发布或被禁用。\n"
		"\bt2. 禁止自己投票或投票欺诈。\bw 这指注册多个账号给自己的或他人的存档投票。我们严格执行本规则，因此你应当明白申诉成功率极低。请确保你与其它账号不在同一家庭网络下投票。所有小号将被永久封禁，主账号将被临时封禁，受影响的存档将被禁用。\n"
		"\bt3. 任何形式的索要投票都不受欢迎。\bw 这类存档会被取消发布，直到问题修复。属于本规则的情况例如：\n"
		   "- 暗示他人点赞或点踩的标志，例如绿色箭头签名或索要投票。\n"
		   "- 以投票换取东西的噱头，例如「满 100 票我就做个更好的版本」。我们把这类行为定义为「刷票」，任何形式的刷票都不允许。\n"
		   "- 以使用存档为条件索要投票，或出于其它任何理由索要投票，都禁止。\n"
		"\bt4. 请勿刷屏。\bw 如前所述，什么算刷屏没有统一标准，以下情况可能算：\n"
		   "- 短时间内上传或重复上传相似的存档。不要试图绕过系统让别人看到或投票给你的存档，包括上传几乎没有意义的「垃圾」或「空白」存档。这类存档会被取消发布。\n"
		   "- 上传纯文字存档。这类内容通常是公告或求助，而论坛与评论区可以实现同样目的。这类存档会被移出首页。\n"
		   "- 上传「艺术」存档并不严格禁止，但可能被移出首页。我们乐于见到以创意方式使用各种元素的作品；缺乏这些要素（例如纯装饰类存档）通常会被移出首页。\n"
		"\bt5. 请勿上传色情或其它不当内容。这类存档会被删除并导致封禁。\bw\n"
		   "- 包括但不限于：性、毒品、种族主义、过度政治内容，以及任何冒犯或侮辱某一群体的内容。\n"
		   "- 请勿试图绕过本规则。任何直接或间接指向上述概念的内容都属于本规则范围。\n"
		   "- 用其它语言提及这些内容同样禁止，请勿尝试绕过本规则。\n"
		   "- 禁止发布违反本规则的网址或图片，包括个人资料中的链接或文字。\n"
		"\bt6. 严禁用图像转换来作图。\bw 包括使用脚本或任何第三方工具替你绘制或生成存档。使用这类工具制作的存档会被删除，并可能被封禁。\n"
		"\bt7. 尽量减少标志与标记。\bw 这类存档可能被移出首页。本规则限制的内容包括：\n"
		   "- 大量放置标志\n"
		   "- 没有明确用途的标记\n"
		   "- 伪造的更新或通知标记\n"
		   "- 链接到无关的存档\n"
		"\bt8. 请勿设置跑题或不当的标签。\bw 标签的作用只是改善搜索结果，一般应当是对存档的一词描述。成句或主观的标签可能被删除；不当或冒犯性的标签很可能导致封禁。\n"
		"\bt9. 禁止故意造成卡顿或崩溃的存档。\bw 如果多数用户反映该存档导致崩溃或卡顿，即适用本规则。这类存档会被移出首页或被禁用。\n"
		"\bt10. 请勿滥用举报系统。\bw 提交「糟糕的存档」或胡乱填写的举报理由是在浪费我们的时间。除非涉及可能的违规或社区问题，否则请不要举报。如果你认为存档违规或造成社区问题，尽管举报！出于善意的举报绝不会导致封禁。\n"
		"\bt11. 请勿要求把存档从首页撤下。\bw 除非存档违规，否则它会留在首页。艺术类存档也不例外，请不要举报艺术存档。\n"
		"\n"
		"\boR 部分：其它\n"
		"\bw管理员可按其判断解释这些规则。规则并非同等重要，有些执行得更宽松。最终认定是否违规由管理员决定，但我们已经尽力在此覆盖所有不受欢迎的行为。规则更新时会在此帖公告。\n"
		"\n"
		"违反这些规则可能导致帖子或评论被删除、存档被取消发布或禁用、存档被移出首页，严重时会被临时或永久封禁。我们有多种人工与自动措施来执行这些规则。不同管理员对严重程度的判断与处理可能并不一致。\n"
		"\n"
		"如果你对什么算违规有任何疑问，欢迎联系管理员。";

	new InformationMessage("上传规则", rules, true);
}

void ServerSaveActivity::CheckName(String newname)
{
	auto user = Client::Ref().GetAuthUser();
	if (newname.length() && newname == save->GetName() && user && save->GetUserName() == user->Username)
		titleLabel->SetText("修改模拟属性：");
	else
		titleLabel->SetText("上传新模拟：");
}

void ServerSaveActivity::OnTick()
{
	if (thumbnailRenderer)
	{
		thumbnailRenderer->Poll();
		if (thumbnailRenderer->GetDone())
		{
			thumbnail = thumbnailRenderer->Finish();
			thumbnailRenderer = nullptr;
		}
	}

	if (uploadSaveRequest && uploadSaveRequest->CheckDone())
	{
		okayButton->Enabled = true;
		try
		{
			save->SetID(uploadSaveRequest->Finish());
			Exit();
			new SaveIDMessage(save->GetID());
			if (onUploaded)
			{
				onUploaded(std::move(save));
			}
		}
		catch (const http::RequestError &ex)
		{
			new ErrorMessage("错误", "上传失败：\n" + ByteString(ex.what()).FromUtf8());
		}
		uploadSaveRequest.reset();
	}

	if(saveUploadTask)
		saveUploadTask->Poll();
}

void ServerSaveActivity::OnDraw()
{
	Graphics * g = GetGraphics();
	g->BlendRGBAImage(saveToServerImage->data(), RectSized(Vec2(-10, 0), saveToServerImage->Size()));
	g->DrawFilledRect(RectSized(Position, Size).Inset(-1), 0x000000_rgb);
	g->DrawRect(RectSized(Position, Size), 0xFFFFFF_rgb);

	if (Size.X > 220)
		g->DrawLine(Position + Vec2(Size.X / 2 - 1, 0), Position + Vec2(Size.X / 2 - 1, Size.Y - 1), 0xFFFFFF_rgb);

	if (thumbnail)
	{
		auto rect = RectSized(Position + Vec2(Size.X / 2 + (Size.X / 2 - thumbnail->Size().X) / 2, 25), thumbnail->Size());
		g->BlendImage(thumbnail->Data(), 0xFF, rect);
		g->DrawRect(rect, 0xB4B4B4_rgb);
	}
}

ServerSaveActivity::~ServerSaveActivity()
{
	if (thumbnailRenderer)
	{
		thumbnailRenderer->Abandon();
	}
	delete saveUploadTask;
}
