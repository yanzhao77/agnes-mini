Agnes Mini 重构开发技术文档 审核报告
文档版本: v2.0 (重构计划) | 审核日期: 2026-07-12 | 审核人: 技术委员会
项目: Agnes Mini SDK | 目标: 剧本分解 → 图片生成 → 视频生成 全流程
基于: Agnes AI API (apihub.agnes-ai.com)

执行摘要
本次审核针对《Agnes Mini 重构开发技术文档》进行全面评估。该文档基于实测数据规划重构方案，包含 6 张参考图生成和视频生成全流程验证结果，数据翔实、问题识别具体。

核心发现：文档基础扎实，问题识别准确，但存在以下关键缺口：

第三阶段设计严重不足：核心价值交付阶段仅有 3 行描述，缺少错误处理、并发策略、状态持久化等设计

视频 API RPM 限制未纳入设计：根据官方文档，免费用户视频模型实际 RPM 为 1 次/分钟，9 镜头场景仅视频生成阶段即需 ≥ 9 分钟，直接影响 Pipeline 架构设计

缺少验收标准与风险清单：无法判断各阶段"完成"的定义

综合评分：7.2/10 | 审核结论：⚠️ 有条件通过（需补充 P0 内容后方可进入开发）

1. 文档概览审核
1.1 基本信息
项目	内容	评估
版本号	v2.0 (重构计划)	✅ 明确
目标描述	"使用 Agnes AI 分解剧本、生成图片和视频"	✅ 清晰
API 引用	apihub.agnes-ai.com	✅ 与官方文档一致
模型版本	agnes-2.0-flash、agnes-image-2.1-flash、agnes-video-v2.0	✅ 正确
1.2 文档结构完整性
章节	状态	评估
1. 项目现状审查	✅ 完整	6 个问题表格化，优先级清晰
2. API 验证结果	✅ 完整	含实测数据，可信度高
3. 重构计划	⚠️ 不完整	第一、二阶段 OK，第三阶段过于简略
4. 新架构设计	✅ 完整	分层图和数据流图清晰
5. 数据模型变更	⚠️ 不完整	缺少 image_prompt、video_prompt 字段
验收标准	❌ 缺失	严重缺失
风险清单	❌ 缺失	严重缺失
测试策略	❌ 缺失	中等缺失
版本兼容性声明	❌ 缺失	中等缺失
2. 问题识别审核
2.1 已识别问题评估
#	问题	严重性	准确性	建议
1	Base URL 配置错误	阻断性	✅ 准确	立即修复 (P0)
2	SSL 证书验证硬编码	高	✅ 准确	新增 verify_ssl: bool = True 配置 (P0)
3	视频查询端点冗余	中	✅ 准确	确认无依赖后移除 (P1)
4	视频响应解析不完整	中	✅ 准确	从 metadata.url 读取，需处理 null (P1)
5	CLI 缺少流式输出	低	⚠️ 优先级存疑	对用户体验重要，建议升 P1
6	Mock Provider 图片 URL 格式	低	✅ 准确	可保持现状，收益低 (P3)
2.2 未识别问题补充
#	遗漏问题	严重性	说明	建议
7	重试逻辑对视频轮询不友好	中	视频轮询是长时操作，429 重试策略应区别于普通请求	为视频 Provider 单独配置重试参数
8	超时配置硬编码	中	base.py 中 timeout=30.0 硬编码	从环境变量读取
9	日志敏感信息泄露风险	低	Debug 模式可能打印 API Key	日志脱敏处理
10	Breaking Change 未声明	高	Base URL 修正确认后影响现有用户	明确版本号策略
11	视频 API RPM 限制未纳入设计	高	免费用户视频模型 1 RPM，直接制约 Pipeline 吞吐量	Pipeline 实现请求节流；向用户明确提示耗时
12	Token Plan 配额限制未考虑	中	Token Plan 用户每日视频配额 500 秒	Pipeline 启动前预检配额
2.3 问题优先级重新评估
优先级	问题编号	数量
🔴 P0	1, 2, 10, 11	4
🟡 P1	3, 4, 5, 7, 8, 12	6
🟢 P2	6, 9	2
3. API 验证结果审核
3.1 测试覆盖度评估
端点	状态	评估
/v1/chat/completions	✅ 已验证	充分
/v1/images/generations	✅ 已验证（6 张）	充分
/v1/videos (POST)	✅ 已验证	充分
/v1/videos/{task_id} (GET)	✅ 已验证	充分
3.2 验证缺口
缺口	建议
并发测试	增加多任务并发场景验证
错误场景	测试无效 prompt、超长任务边界
速率限制	确认实际 RPM 阈值及触发 429 后的恢复时间
图片分辨率兼容性	图片尺寸需为 16 的倍数，否则返回 500 错误
4. 重构计划审核
4.1 第一阶段：修复连接问题（1天）
修改项	评估	风险
config.py:16 Base URL 修改	✅ 明确	低
新增 verify_ssl 配置	✅ 方向正确	中（需明确默认 True）
base.py:43 传入 verify	✅ 正确	低
移除 /agnesapi 备用端点	✅ 正确	中（需确认无其他依赖）
从 metadata.url 读取 URL	✅ 正确	中（需处理 status != completed 时 metadata 为 null）
4.2 第二阶段：增强功能（2天）
新增项	评估	问题
ScriptAgent	⚠️ 描述不足	缺少输入格式、Prompt 设计、解析失败容错
script.py 数据模型	⚠️ 字段不全	缺少 image_prompt、video_prompt 字段
script decompose CLI	⚠️ 描述不足	未说明输出格式和位置
chat 流式输出	✅ 合理	建议升为 P1
建议补充的数据模型：

python
class Shot(BaseModel):
    shot_number: int
    description: str                     # 镜头描述
    image_prompt: str                    # 🆕 用于生成参考图的 prompt
    video_prompt: str                    # 🆕 用于生成视频的 prompt
    camera_angle: str | None = None
    duration: float
    sound: str | None = None
    dialog: str | None = None
    reference_image_url: str | None = None  # 生成的参考图 URL
    video_url: str | None = None             # 生成的视频 URL
    status: str = "pending"                  # pending/generating/completed/failed
4.3 第三阶段：全流程集成（2天）—— ⚠️ 严重不足
问题	说明	建议
错误处理未定义	9 个镜头中 1 个失败，整体继续还是终止？	定义 fail_fast 或 continue_on_error 策略
并行策略未定义	受 1 RPM 限制，无法并行提交视频	设计为串行提交，间隔 ≥ 60 秒
断点恢复未设计	生成到第 5 个镜头时崩溃，能否恢复？	增加中间状态持久化（JSON 缓存）
最终拼接边界不清	"后期拼接 + 声音合成"由谁完成？	明确 SDK 边界，或输出片段 + 拼接脚本
成本估算未提供	9 镜头 × 1 图 + 9 视频 ≈ 18 次调用	预估 API 成本和时间
建议补充的 Pipeline 节流设计：

python
class VideoRateLimiter:
    """视频 API 1 RPM 限流器[citation:1]"""
    def __init__(self, rpm: int = 1):
        self.interval = 60.0 / rpm  # 60秒
        self.last_request_time = 0
        
    async def acquire(self):
        now = time.time()
        wait_time = self.interval - (now - self.last_request_time)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self.last_request_time = time.time()
5. 视频 API 速率限制深度分析（关键新增）
5.1 官方限制数据
根据 Agnes AI Token Plan FAQ 和 Model Catalog：

用户类型	文本模型 RPM	图片模型 RPM	视频模型实际 RPM	视频每日配额
免费/默认	20	分辨率分档	1	取决于 Token Plan
Enterprise	40	更高	2	取决于 Token Plan
Token Plan	1,000	更高	5	500 秒/天
关键说明：

视频模型同时受 RPM 限制 和 每日秒数配额 双重约束

免费用户视频模型 1 次/分钟 为实际可执行 RPM

Token Plan 用户每日视频配额固定为 500 秒

5.2 对 Pipeline 架构的影响
影响维度	具体说明	应对措施
生成耗时	9 视频在 1 RPM 下至少需要 9 分钟（不含生成时间）	Pipeline 实现请求节流；CLI 显示进度和预计时间
并发策略	无法并行提交多个视频任务	第三阶段设计为串行提交，非并行
错误重试	触发 429 时需等待完整分钟周期	实现基于时间窗口的退避重试
配额预检	Token Plan 用户 500 秒/天可能不足	启动前检查配额，提前告警
用户体验	等待时间远超预期（≥ 10 分钟）	文档和 CLI 中明确告知耗时预期
5.3 与现有设计冲突
冲突项	原设计	受 RPM 限制后的调整
第三阶段并行策略	未定义（隐含可并行）	必须明确为串行
单镜头耗时预期	未提及	需标注：≥ 1 分钟/镜头
Pipeline 完成时间	无预期	需标注：9 镜头 ≥ 10-15 分钟
轮询频率	未定义	优化轮询间隔，避免额外消耗
6. 架构设计审核
6.1 分层架构评估
text
CLI + Skill 层    ← ✅ 清晰，但 Pipeline 归属不明确
Agent 层          ← ✅ 合理，新增 ScriptAgent
Provider 层       ← ✅ 需修改视频端点
Models 层         ← ⚠️ 需补充 script.py
基础设施           ← ✅ 需修改 config.py
6.2 数据流评估
评估维度	意见
流程完整性	✅ 端到端覆盖
数据依赖	✅ 清晰（参考图 → 视频，串行依赖）
并行机会	⚠️ 参考图可并行，但视频受 1 RPM 限制必须串行
失败恢复	❌ 未标注
状态持久化	❌ 无
配额预检	❌ 无
7. 风险与问题清单
7.1 技术风险
#	风险描述	概率	影响	缓解措施
R1	API 限流（1 RPM）导致视频生成耗时 ≥ 9 分钟	高	高	Pipeline 实现请求节流；CLI 进度提示；文档说明
R2	Token Plan 500 秒/天配额不足	中	中	Pipeline 启动前预检配额，超出时告警
R3	ScriptAgent 解析剧本不稳定	中	高	设计 prompt 模板 + 解析失败 fallback
R4	SSL 配置不当导致生产环境连接失败	低	高	默认启用验证，提供关闭选项
R5	重构期间 API 行为变更	低	中	增加集成测试，关注官方更新日志
R6	图片尺寸非 16 倍数导致 500 错误	中	低	Model 层增加尺寸校验
7.2 项目风险
#	风险描述	概率	影响	缓解措施
R7	5 天工期不足（第三阶段未细化）	高	高	细化后重新评估，预留 buffer
R8	视频拼接/音频能力需依赖第三方	中	中	明确边界，可输出片段 + 拼接脚本
R9	测试覆盖率从 70.5% 下降	中	低	新增模块设置覆盖率目标 ≥ 65%
R10	用户对长时等待预期管理不足	高	中	CLI 和文档明确告知：9镜头 ≈ 10-15 分钟
8. 改进建议
8.1 必须补充内容（P0）
#	补充项	说明
1	第三阶段详细设计	错误处理、串行提交（受 1 RPM 限制）、状态持久化、边界定义
2	验收标准	各阶段完成条件和验证方式
3	Shot.image_prompt 和 Shot.video_prompt	数据模型字段补充
4	Breaking Change 声明	Base URL 修正的版本策略（建议 v2.0.0）
5	视频 RPM 限制应对方案	Pipeline 节流逻辑 + 用户耗时预估 + 文档说明
6	配额预检逻辑	Pipeline 启动前检查用户配额（RPM 和每日秒数）
8.2 建议补充内容（P1）
#	补充项	说明
7	测试计划	新增模块的测试策略和覆盖率目标
8	风险清单	纳入本报告第 7 章的风险项
9	环境变量变更	新增 VERIFY_SSL、TIMEOUT、VIDEO_RPM 等变量说明
10	成本估算	9 镜头场景的预估 API 费用和时间
11	ScriptAgent Prompt 设计	具体 prompt 模板和解析策略
8.3 优化建议（P2）
#	优化项	说明
12	超时配置暴露	timeout 从环境变量读取
13	日志脱敏	Debug 模式下隐藏 API Key
14	进度回调	Pipeline 增加 on_progress 回调支持
15	图片尺寸校验	确保尺寸为 16 的倍数，避免 500 错误
9. 验收标准建议
9.1 第一阶段验收
AGNES_BASE_URL 默认指向 https://apihub.agnes-ai.com

verify_ssl 配置生效，默认 True

视频查询仅使用 /v1/videos/{task_id}，移除备用端点

视频响应正确从 metadata.url 读取 URL（处理 null）

pytest tests/ 全部通过

9.2 第二阶段验收
ScriptAgent 能成功解析 Seedance 2.0 格式剧本为 Shot 列表

每个 Shot 包含 image_prompt 和 video_prompt

script decompose CLI 输出 JSON 格式结果

agnes chat --stream 支持流式输出

9.3 第三阶段验收
pipeline.py 端到端完成：剧本 → 9 图 → 9 视频

视频请求遵守 1 RPM 限制，间隔 ≥ 60 秒

CLI 显示进度和预计剩余时间

启动前预检配额，配额不足时告警

单镜头失败不影响其他镜头（continue_on_error）

支持断点恢复（中间状态缓存）

输出包含所有生成资源的 URL 列表

10. 审核结论
10.1 审核状态
状态	说明
⚠️ 有条件通过	需在开发启动前补充 P0 级别缺失内容（共 6 项）
10.2 前置条件
在进入开发前，必须完成以下事项：

补充第三阶段详细设计：包含错误处理、串行提交策略（1 RPM 约束）、状态持久化、边界定义

补充验收标准：各阶段完成条件和验证方式

修改 Shot 数据模型：增加 image_prompt 和 video_prompt 字段

声明 Breaking Change：明确版本号策略（建议 v2.0.0）

新增风险清单：纳入本报告第 7 章全部风险项

设计并实现视频请求节流机制：确保 Pipeline 遵守 1 RPM 限制

实现配额预检：Token Plan 用户 500 秒/天配额，启动前检查

更新用户文档：明确告知 9 镜头场景预估耗时（≥ 10-15 分钟）

10.3 建议
补充完成后重新评审：修订版提交技术委员会复核

分阶段实施，逐阶段验收：不建议一次性合并全部变更

持续关注官方更新：模型可用性、速率限制、配额规则可能变化，生产环境前确认最新值

附录 A：Agnes AI 视频 API 速率限制详细说明
A.1 官方限制数据
根据 Token Plan FAQ 和 Model Catalog：

模型类型	用户类型	允许发起 RPM	实际 RPM	每日配额
视频模型	default	2	1	取决于 Token Plan
视频模型	enterprise	2	2	取决于 Token Plan
视频模型	TokenPlan	6	5	500 秒/天
A.2 对 SDK 设计的约束
视频生成必须串行：免费用户 1 RPM 限制下，多镜头并行提交会立即触发限流

轮询策略需优化：每 60 秒最多发起 1 次视频创建请求

用户体验透明化：CLI 应显示"等待 60 秒后可提交下一个视频请求"等提示

配额保护：Token Plan 用户 500 秒/天配额需在 Pipeline 启动前预检

A.3 实际场景耗时估算
场景	镜头数	最小耗时（仅提交）	含视频生成时间
短视频（3 镜头）	3	3 分钟	5-8 分钟
标准短片（9 镜头）	9	9 分钟	12-18 分钟
Token Plan 用户（9 镜头）	9	1.8 分钟	5-10 分钟
附录 B：审核检查清单
维度	结果
文档结构完整	⚠️ 缺失验收标准、风险清单
技术方案可行	✅ 基于已验证 API
问题识别准确	✅ 6 个核心问题准确
计划可执行	⚠️ 第三阶段不足
数据模型完整	⚠️ 缺少 prompt 字段
API 速率限制考虑	❌ 原文档未考虑，已在本报告中补充
风险已识别	❌ 原文档未识别
验收标准明确	❌ 未定义
版本策略清晰	❌ 未声明
附录 C：参考文档
Agnes Mini 技术文档 v1.0.0

Agnes AI Token Plan FAQ

Agnes AI Model Catalog

Agnes AI 概述文档

Agnes AI FAQs

报告结束