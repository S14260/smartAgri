# 协作约定

面向本仓库的所有成员。目标是四五个人的小组也能保持 `main` 随时可跑、历史可读、出问题能定位。

---

## 一、三条红线

违反这三条，恢复成本远高于遵守成本。

**1. 不直接往 `main` 推代码**

`main` 是永远处于可运行状态的基线。所有改动走功能分支 + Pull Request。

**2. 密钥、密码、token 不入库**

已经发生过：`application.yml`（含数据库密码）和前端页面里的高德/天地图 Key 曾被提交。
- `src/main/resources/application.yml` 已在 `.gitignore` 里，**保持这样**
- 前端页面里的地图 Key 不要写死，改走配置
- 提交前自查：`git diff --cached | grep -iE "password|secret|api[_-]?key|token"`

**3. 大文件不入库**

模型权重、训练产物、数据集、虚拟环境、视频一律不进 git。git 会把它们永久留在历史里，之后每个人 clone 都要下载。

已经在 `.gitignore` 里挡住的：`*.pt`、`runs/` 下的图片与 json、`__pycache__/`、`venv/`、`*.log`、`*.pid`。

提交前自查仓库体积：
```bash
git count-objects -vH          # 看 size-pack
du -sh .git
```
当前仓库内容约 100 MB。**单个 PR 如果让仓库增长超过 10 MB，先在群里说一下。**

例外：`api/farm_field_detection/best.pt`（推理必需）和
`runs/segment/field_segmentation/weights/best.pt`（训练成果）在 `.gitignore` 里用 `!` 白名单放行，别动这两条规则。

---

## 二、分支命名

一个分支只做一件事。分支名用 `类型/简述`，涉及多人并行时带上自己的名字。

```bash
git switch -c feat/ndvi-export
git switch -c fix/tab-active-mask
git switch -c feat/patrol-route-lijia     # 重名风险高时带名字
```

常用类型：`feat` 新功能、`fix` 修 bug、`refactor` 重构、`docs` 文档、`chore` 杂项。

---

## 三、提交信息

**格式**：`类型: 简述`，一行说清做了什么。

```
feat: 新增 NDVI 导出接口
fix: 修复控制台 tab 选中态遮挡文字
docs: 补充 Flask 服务启动说明
refactor: 抽出分页工具类
```

不好的写法：`更新`、`修改一下`、`项目展示更新`、`提交`。
半年后没人知道 `项目展示更新` 改了什么、要不要回滚。

一次提交只做一件事。顺手改了无关文件就拆成两个提交，回滚时不用纠结。

---

## 四、日常流程

```bash
# 1. 开工前先同步，避免在旧代码上开发
git switch main
git pull --rebase origin main

# 2. 开分支干活
git switch -c feat/xxx
# ... 改代码 ...
git add <具体文件>          # 不要用 git add -A，容易误加临时文件
git commit -m "feat: xxx"

# 3. 推送
git push -u origin feat/xxx
```

然后在 GitHub 上开 Pull Request，找一个人 review。

**冲突处理**：谁后合并谁负责解决。解决方式是
```bash
git fetch origin
git rebase origin/main      # 在功能分支上 rebase，不要 merge main 进来
# 解决冲突 → git add → git rebase --continue
git push --force-with-lease origin feat/xxx
```
`--force-with-lease` 比 `--force` 安全：如果远端在你上次 fetch 之后有了新提交，它会拒绝推送，不会覆盖别人的东西。

---

## 五、Pull Request 与合并

- PR 标题写清楚做什么，描述里写**为什么改**和**怎么验证的**
- 至少 1 人 review 通过后再合并
- **合并方式统一用 Squash merge**：一个 PR 压成一个提交落到 `main`，历史干净，回滚方便
- 合并前确认 CI/本地能跑通

> 仓库管理员请在 GitHub 上配置分支保护：
> `Settings → Branches → Add branch protection rule`，target 填 `main`，勾选
> **Require a pull request before merging**（至少 1 个 approval）
> 和 **Require branches to be up to date before merging**。

---

## 六、数据库变更

数据库结构是四个人最容易搞乱的地方。

**规则：谁改表，谁在同一次 PR 里更新 `src/main/resources/mydb.sql`**，并在 PR 描述里写清迁移步骤。

```sql
-- 例：新增字段
ALTER TABLE admin_plots ADD COLUMN soil_type VARCHAR(32) DEFAULT NULL COMMENT '土壤类型';
```

新人上手时必须能靠 `mydb.sql` 建出和别人一致的库。如果你在本地手改了表结构却没更新脚本，别人的库就会悄悄不一致，然后在某个莫名其妙的查询上报错。

---

## 七、新人上手

```bash
git clone https://github.com/S14260/smartAgri.git
cd smartAgri
```

然后按 `README.md` 的「快速开始」走。三个容易卡住的地方：

1. **数据库**：`mysql -u root -p mydb < src/main/resources/mydb.sql`
2. **`application.yml` 不在仓库里**（含密码，被 gitignore）。从 README 的模板复制一份到
   `src/main/resources/application.yml` 再填自己的配置。
3. **计算层不用你启动**。Python 计算层（Flask :8000）已经部署在 `123.56.228.32`，代码里的
   地址默认就指向它。建库 + 配好 `application.yml` + 起 Java 后端，功能就是完整的。
   只有要改 `api/` 下的算法或路由时才需要本地启动——届时入口是 `api/ndvi/app.py` 和
   `api/farm_field_detection/app.py`（**不是** `api/app.py`），并且要记得改服务地址、
   别把本地地址提交上去。

---

## 八、与其他组系统对接

对外接口的返回格式、鉴权方式、接口清单见 `docs/api-contract.md`。

对接原则：**先定接口，再写代码**。双方按 `docs/api-contract.md` 的契约各写各的、用假数据并行开发，最后联调，而不是等两边都写完了再凑。

改接口时在路径上加版本号（`/v1/...`），新接口上线后旧接口先保留一段时间再下线，避免对方突然挂掉。
