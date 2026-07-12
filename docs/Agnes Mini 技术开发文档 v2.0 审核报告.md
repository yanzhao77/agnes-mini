Agnes Mini 技术开发文档 v2.0 审核报告
文档版本: v2.0 | 审核日期: 2026-07-12 | 审核人: 技术委员会
核心关注: 角色与场景一致性 | 目标: 从剧本到视频的完整管线
审核结论: ✅ 通过 — 技术方案完全可行，建议按 P0 建议优化后进入开发

执行摘要
本次审核针对《Agnes Mini 技术开发文档 v2.0》进行评估。该文档聚焦于解决 v1.0 管线中角色、场景、道具、光照不一致的核心问题，提出了通过建立参考图库 + image-to-image 机制强制保持视觉一致性的技术方案。

核心发现：通过与 Agnes AI 官方文档和模型目录的对照验证，v2.0 方案中的两项关键技术前提均已确认支持：

技术前提	官方文档验证	状态
Image-to-image 支持	Agnes Image 2.1 Flash 支持 extra_body.image 参数，可传入 URL 或 Data URI 	✅ 确认
视频图生视频支持	Agnes Video V2.0 支持 image 参数（单图或数组），支持 ti2vid 和 keyframes 模式 	✅ 确认
多图视频	Video API 支持 image 数组和 extra_body.image 多图输入 	✅ 确认
视频查询端点	官方推荐使用 video_id 查询：GET /agnesapi?video_id={id} 	✅ 确认
综合评分：8.5/10

审核结论：✅ 通过 — 设计思路与您观察的问题完全吻合，技术方案可在 Agnes AI 平台上完整落地。

1. 设计思路确认
1.1 您的观察与文档方案的对应关系
根据您的观察——v1.0 生成的内容在人物一致性方面存在严重问题——v2.0 文档的设计思路与之完全对应：

您的观察	文档方案	对应章节
生成的人物面容、服装不一致	建立角色三视图（前/侧/背）+ 表情特写图库	第 4 章
场景布局、色调不连贯	建立场景基图 + 局部变体图库	第 5 章
各镜头独立生成导致视觉断裂	视频生成时参考已建立的人物和场景图	第 6 章
1.2 设计思路与 API 能力的完整对应
text
您的思路：剧本 → 人物提取 → 人物三视图/表情 → 场景图 → 参考图库 → 视频生成
文档方案：剧本 → ScriptAnalysisAgent → CharacterBank/SceneBank → ReferenceGenerator → ConsistentGenerator → 视频
API 能力：agnes-2.0-flash → agnes-image-2.1-flash (img2img) → agnes-image-2.1-flash (img2img) → agnes-video-v2.0 (ti2vid)
核心验证结论：文档方案与您的设计思路完全一致。Agnes AI 平台原生支持图生图和图生视频，可直接用于构建一致性管线。

2. 核心技术前提验证
2.1 Image-to-image 支持验证
根据 Agnes Image 2.1 Flash 官方文档 ：

参数	说明	验证结果
extra_body.image	输入图像数组，支持公共图像 URL 或 Data URI Base64	✅ 支持
必填条件	图生图任务必填	✅ 已确认
参数位置	在 extra_body 对象中传入	✅ 正确
验证示例 ：

bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Transform the scene into a rainy cyberpunk night while preserving composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["https://example.com/input.png"],
      "response_format": "url"
    }
  }'
2.2 视频图生视频支持验证
根据 Agnes Video V2.0 官方文档 ：

参数	说明	验证结果
image	图片 URL 或图片 URL 数组，用于图生视频	✅ 支持
mode	ti2vid（图生视频）或 keyframes（关键帧）	✅ 支持
异步任务	创建任务后返回 video_id，轮询获取结果	✅ 支持
查询端点	GET https://apihub.agnes-ai.com/agnesapi?video_id={id}	✅ 官方推荐 
创建视频请求示例 ：

bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset",
    "image": "https://example.com/ref.png",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
2.3 官方模型目录验证
根据 Agnes AI 官方模型目录 ：

模型	能力	端点
agnes-image-2.1-flash	文生图、图生图	POST /v1/images/generations
agnes-image-2.0-flash	文生图、图生图、多图合成	POST /v1/images/generations
agnes-video-v2.0	文生视频、图生视频、多图视频、关键帧	POST /v1/videos
关键补充：如果需要多图参考（如同时传入角色+场景参考图），agnes-image-2.0-flash 支持多图合成 ，可作为备选方案。

3. 架构设计审核
3.1 三层管线
层级	功能	所用模型	技术可行性
第一层：剧本分析	输出角色清单 + 场景清单 + 镜头清单	agnes-2.0-flash 	✅ 已验证
第二层：参考图生成	角色三视图 + 表情 + 场景全景	agnes-image-2.1-flash (img2img) 	✅ 已确认
第三层：带参考的镜头生成	使用参考图强制一致性	agnes-image-2.1-flash + agnes-video-v2.0 	✅ 已确认
3.2 完整数据流
text
剧本 → ScriptAnalysisAgent (agnes-2.0-flash)
  → 角色: 爷爷/孙女 (含外貌描述)
  → 场景: 厨房 (含布局描述)
  → 镜头: 9 个

ReferenceGenerator
  → 爷爷基图 (text-to-image)
  → 爷爷三视图 + 表情变体 (image-to-image, extra_body.image)
  → 孙女基图 + 三视图 + 表情变体 (image-to-image)
  → 厨房全景 + 局部变体 (image-to-image)

ConsistentGenerator
  遍历 9 个镜头:
    1. 取角色参考图 + 场景参考图
    2. 生图: extra_body.image = [角色参考图, 场景参考图] (需使用 agnes-image-2.0-flash 支持多图)
    3. 生视频: image = 角色参考图 (使用 agnes-video-v2.0)
3.3 与 v1.0 的集成策略（建议）
维度	建议策略
版本关系	v2.0 作为 v1.0 的扩展，新增 ConsistentPipeline 类，用户可选择使用
数据模型	Shot 模型保持不动，新增 ShotV2 继承 Shot，增加 character_refs 和 scene_ref
CLI	新增 agnes pipeline v2 run 子命令，agnes pipeline run 保持 v1.0 行为
测试兼容	v1.0 现有测试全部保留，v2.0 新增独立测试模块
4. 数据模型审核
4.1 角色模型 (CharacterBank)
字段	评估
name, base_description, base_image_url	✅ 合理
views[] (front/side/back/three_quarter)	✅ 建议统一包含 four views
expressions[] (neutral/happy/sad/surprised/thoughtful)	✅ 合理
建议：文档 4.2 节提到 three_quarter_view，但第 3 章模型定义中未包含，建议统一。

4.2 场景模型 (SceneBank)
字段	评估
name, base_description, base_image_url	✅ 合理
variants[] (wide_full/corner_stove/window_view/table_close)	✅ 合理
4.3 扩充镜头模型 (ShotV2)
字段	评估
character_refs[], scene_ref	✅ 合理
image_prompt, video_prompt	✅ 合理
reference_image_status	⚠️ 建议新增，追踪参考图生成进度
5. API 调用量精确计算（P0 建议补充）
类型	数量	调用次数
剧本分析	1 次	1
角色基图（2 角色）	2 张	2
角色视图变体（2 角色 × 4 视图）	8 张	8
角色表情变体（2 角色 × 5 表情）	10 张	10
场景基图	1 张	1
场景局部变体	4 张	4
镜头参考图（9 镜头 × 1 张）	9 张	9
镜头视频（9 镜头）	9 段	9
合计	34 次图片 + 9 次视频 + 1 次文本 = 44 次 API 调用	
与 v1.0 对比：v2.0 调用量约为 v1.0（18 次）的 2.4 倍 。

6. 对 1 RPM 限制的影响
场景	v1.0	v2.0
图片调用（无限制）	9 次	34 次
视频调用（1 RPM）	9 次，≥ 9 分钟	9 次，≥ 9 分钟
总耗时	约 10 分钟	约 12-18 分钟（含参考图生成）
结论：视频生成仍是主要瓶颈（受 1 RPM 限制），新增的 25 次图片调用对总耗时影响有限，因为图片调用可并行提交。

7. 视频查询端点重要提示
根据 Agnes AI 模型目录 ：

视频查询请使用 video_id，不要使用 task_id 查询当前视频结果，除非旧版工作流明确要求。

端点	方法	说明
GET https://apihub.agnes-ai.com/agnesapi?video_id={id}	✅ 官方推荐	查询视频结果
GET /v1/videos/{task_id}	⚠️ 谨慎使用	可能不适用于当前版本
文档 v2.0 第 6.1 节使用 POST /v1/videos 创建任务，建议补充使用 video_id 而非 task_id 查询结果的说明。

8. 风险清单
#	风险描述	概率	影响	缓解措施
R1	API 限流(1 RPM)致 9 镜头 ≥ 9 分钟	高	高	Pipeline 节流 + CLI 进度提示
R2	Token Plan 500s/天配额不足	中	中	启动前预检, 超配额告警
R3	ScriptAnalysisAgent 解析剧本不稳定	中	高	prompt 模板 + 重试 + fallback
R4	image-to-image 风格迁移不准确	中	中	多图参考 + 手动优选 
R5	视频生成时长 + 图生图调用激增	中	中	文档中明确成本 trade-off
R6	多图参考需要使用 agnes-image-2.0-flash	低	低	文档中注明版本选择 
9. 改进建议汇总
9.1 必须补充内容（P0）
#	补充项	说明
1	视频查询使用 video_id 端点	官方推荐 GET /agnesapi?video_id={id} 
2	精确计算 API 调用量和预估成本	44 次调用（34 图 + 9 视频 + 1 文本）
3	多图参考需使用 agnes-image-2.0-flash	2.1-Flash 支持单图图生图，多图合成建议用 2.0-Flash 
4	与 v1.0 的集成策略	明确是替换、扩展还是并行分支
9.2 建议补充内容（P1）
#	补充项	说明
5	统一角色视图类型定义	含 three_quarter_view
6	补充 ShotV2.reference_image_status 字段	追踪参考图生成进度
7	图生图 Prompt 结构指导	参考官方建议："改什么" + "保什么" 
8	视频生成参数优化建议	num_frames 需遵循 8n+1 规则，≤441 
10. 审核结论
10.1 审核状态
项目	结论
文档版本	v2.0
设计思路	✅ 与您的观察完全吻合
技术方案	✅ 业界成熟方案
Agnes AI 平台支持	✅ 图生图 + 图生视频均已确认支持
审核结论	✅ 通过
10.2 关键验证结论
验证项	结果
Image-to-image (extra_body.image)	✅ 官方文档确认支持 
视频图生视频 (image 参数)	✅ 官方文档确认支持 
多图视频合成	✅ 支持 image 数组 
视频查询端点	✅ 使用 video_id 查询 /agnesapi 
10.3 设计确认
您的设计思路——提取人物 → 三视图/表情图 → 场景图 → 参考生成——已在文档中正确实现，且 Agnes AI 平台原生支持所需的所有 API 能力。

建议在开发启动前补充 P0 的 4 项内容，然后按计划推进开发。