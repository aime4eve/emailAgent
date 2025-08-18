# DDD 重构实践指南：从单体到分层架构

## 1. 引言

本文档旨在通过一个实际项目的重构案例，展示如何将一个传统的单体应用逐步演进为基于领域驱动设计（DDD）思想的分层架构。通过对比重构前后的项目结构和代码组织方式，我们希望能为其他项目的架构升级提供一套清晰、可操作的实践指南。

DDD 的核心思想是将业务领域的复杂性作为设计的核心，通过限界上下文（Bounded Context）和分层架构（Layered Architecture）来隔离关注点，降低系统耦合度，提升代码的可维护性和可扩展性。

## 2. 重构前：传统的单体结构

在重构之前，项目采用的是一种常见的单体结构，所有模块都直接放置在 `src` 目录下，缺乏明确的边界和分层。

### 2.1. 原始目录结构

```
d:\emailAgent/
├── src/
│   ├── email/              # 邮件处理模块，职责比较模糊
│   │   ├── __init__.py
│   │   ├── email_receiver.py # 包含邮件接收和处理的主要逻辑
│   │   └── pop3_adapter.py   # 具体的 POP3 协议实现，技术实现与业务逻辑混合
│   ├── knowledge_graph/    # 知识图谱模块，定义了图的结构和本体
│   │   ├── __init__.py
│   │   ├── node.py         # 定义图的节点
│   │   ├── edge.py         # 定义图的边
│   │   ├── graph.py        # 定义图的数据结构
│   │   ├── ontology.py     # 定义本体论相关操作
│   │   └── ontology_generator.py # 本体生成逻辑，业务代码
│   ├── utils/              # 通用工具和配置模块，但位置分散
│   │   ├── __init__.py
│   │   ├── config.py       # 项目配置
│   │   └── data_loader.py  # 数据加载工具
│   ├── web_app/            # Web 应用模块
│   │   ├── __init__.py
│   │   ├── web_app_main.py # Web 服务启动入口
│   │   └── interaction_handler.py # 处理用户交互，与业务逻辑强耦合
│   └── visualization/      # 可视化模块
│       └── plotly_graph.py # 具体的图表库实现，直接依赖 `knowledge_graph` 内部
├── tests/                  # 测试目录，结构单一，未与源码结构对应
│   └── test_email_receiver.py # 零散的测试文件
├── main_entry.py           # 项目主入口文件
└── requirements.txt        # Python 依赖包列表
```

### 2.2. 存在的问题

- **职责不清**：`email`、`knowledge_graph`、`web_app` 等模块混合在一起，业务逻辑、技术实现和UI代码相互交织。
- **高耦合度**：模块之间直接相互依赖，例如 `visualization` 直接依赖 `knowledge_graph` 的内部实现，任何一方的改动都可能影响另一方。
- **可维护性差**：随着业务逻辑的增长，代码会变得越来越难以理解和维护。`utils` 和 `config` 等通用模块散落在各处，缺乏统一管理。
- **测试困难**：由于模块间紧密耦合，编写单元测试和集成测试变得非常困难。

## 3. 重构后：基于 DDD 的分层架构

重构的核心目标是引入 DDD 的限界上下文和分层架构，将系统拆分为多个高内聚、低耦合的模块。

### 3.1. 新的目录结构

```
d:\emailAgent/
├── src/                                      # 源代码根目录
│   ├── email_ingestion/ (限界上下文)        # 邮件接收限界上下文，封装所有与邮件处理相关的业务
│   │   ├── application/                    # 应用层：编排领域服务，处理用例流程
│   │   │   └── email_service.py            # 邮件应用服务，如 fetch_and_process_emails
│   │   ├── domain/                         # 领域层：包含核心业务模型和逻辑，不依赖任何其他层
│   │   │   ├── model/                      # 领域模型，定义业务核心实体
│   │   │   │   └── email.py                # Email 实体，定义邮件的核心属性和行为
│   │   │   └── repository/                 # 仓储接口，定义数据持久化的抽象
│   │   │       └── email_repository.py     # 定义 Email 仓储的抽象接口（如 save, find）
│   │   └── infrastructure/                 # 基础设施层：实现外部依赖，如数据库、API适配器
│   │       ├── pop3_adapter.py             # POP3 适配器，实现与邮件服务器的通信
│   │       └── file_email_repository.py    # 文件系统实现的 Email 仓储，用于本地存储
│   ├── knowledge_management/ (限界上下文)    # 知识管理限界上下文，负责知识图谱的构建和管理
│   │   ├── application/                    # 应用层
│   │   │   └── ontology_generator.py       # 本体生成器应用服务，协调领域对象完成任务
│   │   ├── domain/                         # 领域层
│   │   │   ├── model/                      # 领域模型
│   │   │   │   ├── node.py                 # 知识图谱的节点实体
│   │   │   │   ├── edge.py                 # 知识图谱的边实体
│   │   │   │   └── graph.py                # 知识图谱的图聚合根
│   │   │   └── repository/                 # 仓储接口
│   │   │       └── knowledge_graph_repository.py # 知识图谱仓储的抽象接口
│   │   └── infrastructure/                 # 基础设施层
│   │       └── file_knowledge_graph_repository.py # 文件系统实现的知识图谱仓储
│   ├── interfaces/ (接口层)                # 接口层，负责与外部系统（如Web、CLI）交互
│   │   └── web_app/                        # Web应用，作为一种外部接口
│   │       ├── web_app_main.py             # Web 应用主入口，依赖应用层服务
│   │       ├── interaction_handler.py      # 用户交互处理器
│   │       └── visualization/              # 可视化组件
│   │           └── plotly_graph.py         # 使用 Plotly 实现的图谱可视化
│   └── shared/ (共享内核)                  # 共享内核，存放跨上下文的通用代码
│       ├── config.py                       # 全局配置文件
│       └── utils/                          # 通用工具类
│           └── data_loader.py              # 数据加载工具
├── tests/                                  # 测试目录，结构与 src 目录对齐，便于管理
│   ├── email_ingestion/                    # email_ingestion 限界上下文的单元测试和集成测试
│   └── knowledge_management/               # knowledge_management 限界上下文的测试
├── main_entry.py                           # 项目主入口文件
└── requirements.txt                        # Python 依赖包列表
```

### 3.2. 核心概念解读

- **限界上下文 (Bounded Context)**：我们将系统拆分为两个核心的限界上下文：
    - `email_ingestion`：负责所有与邮件接收、解析和初步处理相关的业务。
    - `knowledge_management`：负责知识图谱的构建、管理和操作。
    每个限界上下文都有自己独立的领域模型和业务逻辑，彼此之间通过明确的接口进行通信。

- **分层架构 (Layered Architecture)**：在每个限界上下文中，我们都遵循了经典的分层架构：
    - **Domain (领域层)**：包含核心的业务逻辑和领域模型（如 `Email`、`KnowledgeGraph`），以及仓储接口（`EmailRepository`）。这是业务的核心，不依赖任何其他层。
    - **Application (应用层)**：负责协调领域对象来完成具体的业务场景（用例），例如 `EmailAppService`。它依赖领域层。
    - **Infrastructure (基础设施层)**：提供通用的技术能力，例如数据库访问、文件系统操作、第三方服务集成等。这里我们实现了仓储接口（`FileEmailRepository`）和外部服务的适配器（`POP3Adapter`）。它依赖领域层（实现接口）。
    - **Interfaces (接口层)**：负责与外部系统进行交互，例如 Web API、Web UI 等。我们将 `web_app` 和 `visualization` 放在这一层，它们依赖应用层来发起业务操作。

- **共享内核 (Shared Kernel)**：对于跨限界上下文的通用模块，例如配置文件 `config.py` 和工具类 `utils`，我们将其提取到 `shared` 目录中，作为共享内核。

## 4. 模块迁移路径对比

| 原始模块/文件 | 原始路径 | 重构后模块/文件 | 重构后路径 | 重构说明 |
| --- | --- | --- | --- | --- |
| `email` | `src/email` | `email_ingestion` | `src/email_ingestion` | 形成独立的限界上下文，负责邮件处理。 |
| `knowledge_graph` | `src/knowledge_graph` | `knowledge_management` | `src/knowledge_management` | 形成独立的限界上下文，负责知识图谱管理。 |
| `web_app` | `src/web_app` | `web_app` | `src/interfaces/web_app` | 归入接口层，负责对外提供Web服务。 |
| `visualization` | `src/visualization` | `visualization` | `src/interfaces/web_app/visualization` | 作为Web应用的一部分，归入接口层。 |
| `config.py` | `src/utils/config.py` | `config.py` | `src/shared/config.py` | 归入共享内核，供所有模块使用。 |
| `utils` | `src/utils` | `utils` | `src/shared/utils` | 通用工具类归入共享内核。 |
| `tests` | `tests/` | `tests` | `tests/` | 测试目录结构与 `src` 保持一致，便于定位和管理。 |

## 5. 代码迁移示例：以 `Email` 模块为例

为了更具体地展示重构过程，我们以原始的 `email` 模块为例，看看它的代码是如何被拆分和迁移到新的 `email_ingestion` 限界上下文中的。

### 5.1. 迁移前：混合的业务逻辑与技术实现

在原始结构中，`src/email/email_receiver.py` 文件可能看起来像这样，它混合了数据结构、业务逻辑和对外部服务（POP3）的直接调用。

```python
# src/email/email_receiver.py (原始文件)
import poplib
from email.parser import Parser

# 直接依赖具体实现
from .pop3_adapter import POP3Adapter 

# 配置信息硬编码或来自全局
POP3_SERVER = 'pop.example.com'
POP3_USER = 'user'
POP3_PASS = 'password'

class EmailReceiver:
    def __init__(self):
        self.pop3_adapter = POP3Adapter(POP3_SERVER, POP3_USER, POP3_PASS)

    def fetch_emails(self):
        """
        连接服务器，获取邮件，解析并返回
        """
        raw_emails = self.pop3_adapter.fetch_all()
        parsed_emails = []
        for raw_email in raw_emails:
            # 业务逻辑：解析邮件
            parsed_email = Parser().parsestr(raw_email)
            # 数据结构：直接使用字典
            email_data = {
                'from': parsed_email['from'],
                'to': parsed_email['to'],
                'subject': parsed_email['subject'],
                'body': parsed_email.get_payload(decode=True).decode()
            }
            parsed_emails.append(email_data)
            # 持久化逻辑也可能在这里
            self._save_to_file(email_data)
        return parsed_emails

    def _save_to_file(self, email_data):
        # 直接的文件操作，耦合了存储实现
        with open(f"data/{email_data['subject']}.txt", "w") as f:
            f.write(str(email_data))
```

**问题点**:
*   `EmailReceiver` 类做了太多事：连接、获取、解析、存储。
*   直接依赖 `POP3Adapter`，无法替换为其他邮件源（如 IMAP）。
*   邮件的数据结构是一个简单的字典，没有行为，是贫血模型。
*   持久化逻辑 `_save_to_file` 硬编码在服务类中。

### 5.2. 迁移后：职责清晰的分层架构

重构后，上述功能被拆分到 `email_ingestion` 限界上下文的不同层级中。

**1. 领域层 (Domain Layer)**: 定义核心业务对象和规则。

*   **`src/email_ingestion/domain/model/email.py` (领域模型)**
    *   定义 `Email` 实体，封装邮件的核心数据和行为。

    ```python
    # src/email_ingestion/domain/model/email.py
    from dataclasses import dataclass

    @dataclass
    class Email:
        id: str
        sender: str
        recipient: str
        subject: str
        body: str

        # 未来可以添加领域行为，例如:
        # def is_spam(self):
        #     return "spam" in self.subject.lower()
    ```

*   **`src/email_ingestion/domain/repository/email_repository.py` (仓储接口)**
    *   定义持久化的抽象，领域层不关心如何实现。

    ```python
    # src/email_ingestion/domain/repository/email_repository.py
    from abc import ABC, abstractmethod
    from .model.email import Email

    class IEmailRepository(ABC):
        @abstractmethod
        def save(self, email: Email):
            pass

        @abstractmethod
        def find_by_id(self, email_id: str) -> Email | None:
            pass
    ```

**2. 基础设施层 (Infrastructure Layer)**: 实现技术细节。

*   **`src/email_ingestion/infrastructure/pop3_adapter.py` (外部服务适配器)**
    *   封装与 POP3 服务器交互的技术细节。

    ```python
    # src/email_ingestion/infrastructure/pop3_adapter.py
    # (内容与旧版类似，但现在它的职责很纯粹：只负责与POP3服务器通信)
    import poplib

    class POP3Adapter:
        # ... 实现连接、获取、删除邮件等方法 ...
        def fetch_all(self):
            # ... returns list of raw emails
            pass
    ```

*   **`src/email_ingestion/infrastructure/file_email_repository.py` (仓储实现)**
    *   实现领域层定义的仓储接口，负责将 `Email` 对象存入文件系统。

    ```python
    # src/email_ingestion/infrastructure/file_email_repository.py
    from ...domain.model.email import Email
    from ...domain.repository.email_repository import IEmailRepository
    import json

    class FileEmailRepository(IEmailRepository):
        def save(self, email: Email):
            # 将 Email 对象保存为 JSON 文件
            with open(f"data/{email.id}.json", "w") as f:
                json.dump(email.__dict__, f)
        
        def find_by_id(self, email_id: str) -> Email | None:
            # ... 实现从文件加载 ...
            pass
    ```

**3. 应用层 (Application Layer)**: 协调领域对象和基础设施来完成用例。

*   **`src/email_ingestion/application/email_service.py` (应用服务)**
    *   编排整个“获取并处理邮件”的流程。

    ```python
    # src/email_ingestion/application/email_service.py
    from ..domain.repository.email_repository import IEmailRepository
    from ..infrastructure.pop3_adapter import POP3Adapter
    from ..domain.model.email import Email
    from email.parser import Parser
    import uuid

    class EmailAppService:
        def __init__(self, email_repository: IEmailRepository, pop3_adapter: POP3Adapter):
            self.email_repository = email_repository
            self.pop3_adapter = pop3_adapter

        def fetch_and_process_emails(self):
            raw_emails = self.pop3_adapter.fetch_all()
            for raw_email in raw_emails:
                parsed = Parser().parsestr(raw_email)
                
                # 创建领域对象
                email = Email(
                    id=str(uuid.uuid4()),
                    sender=parsed['from'],
                    recipient=parsed['to'],
                    subject=parsed['subject'],
                    body=parsed.get_payload(decode=True).decode()
                )
                
                # 使用仓储进行持久化
                self.email_repository.save(email)
    ```

通过这种方式，我们将一个臃肿的类拆分成了多个各司其职的模块，实现了高内聚、低耦合的目标。

## 6. 关键收益与实践建议

### 6.1. 关键收益

- **高内聚，低耦合**：业务逻辑被封装在各自的限界上下文中，技术实现细节被隔离在基础设施层，使得系统各部分的职责更加清晰。
- **可维护性与可扩展性**：清晰的边界和分层使得修改和扩展功能变得更加容易，降低了引入新 Bug 的风险。
- **贴近业务**：代码结构直接反映了业务领域，使得开发人员和领域专家可以用共通的语言进行交流。
- **可测试性增强**：分层架构使得单元测试和集成测试的编写变得更加简单和高效。

### 6.2. 实践建议

- **从小处着手**：对于大型遗留系统，不必追求一次性完全重构。可以从一个核心的、独立的业务模块开始，将其改造为第一个限界上下文。
- **团队沟通**：DDD 的成功离不开团队对业务领域的深刻理解。定期的领域知识分享和模型讨论会至关重要。
- **不要过度设计**：并非所有模块都需要复杂的领域模型。对于一些简单的 CRUD 操作，使用贫血模型和事务脚本模式可能更为高效。

## 7. 未来功能扩展对比：以“邮件附件处理”为例

为了进一步体现 DDD 架构的优势，我们假设一个未来的新需求：**“系统需要能够处理邮件附件，提取其中的文本内容，并将其作为知识源的一部分。”**

让我们看看在新旧两种架构下，实现这一需求分别需要如何操作。

### 7.1. 在旧架构中扩展

在原始的单体结构中，实现这个功能可能会非常混乱：

1.  **修改 `email_receiver.py`**：你需要打开 `EmailReceiver` 类中的 `fetch_emails` 方法。
2.  **添加附件处理逻辑**：在解析邮件的核心循环中，增加代码来检查 `parsed_email` 是否包含附件。
3.  **引入新的依赖**：可能需要引入一个新的库（如 `pdfplumber` 或 `python-docx`）来解析不同格式的附件（PDF, Word文档等）。这个 `import` 语句会直接加在 `email_receiver.py` 的顶部。
4.  **混合的职责**：`fetch_emails` 方法的职责会进一步膨胀，它现在不仅要获取、解析邮件主体，还要负责解析附件、提取文本。
5.  **修改数据结构**：你需要修改 `email_data` 这个字典，添加一个新的键（如 `attachment_text`）来存储提取的文本。所有使用这个字典的地方可能都需要修改。
6.  **耦合的修改**：如果知识图谱模块需要使用这些文本，你可能需要直接在 `email_receiver.py` 中调用 `knowledge_graph` 模块的函数，从而加深了两个模块之间的耦合。

**痛点**：
*   **单一文件职责过重**：`email_receiver.py` 变成了“上帝类”，几乎无所不包。
*   **核心业务逻辑被污染**：附件处理的技术细节（如用什么库解析PDF）与邮件接收的核心业务逻辑混在一起。
*   **连锁反应**：修改一个功能，需要触及多个不相关的部分，测试也变得更加复杂。

### 7.2. 在新的 DDD 架构中扩展

在 DDD 架构下，这个新需求的实现路径会非常清晰和优雅：

1.  **更新领域模型 (Domain Layer)**：
    *   打开 `src/email_ingestion/domain/model/email.py`。
    *   在 `Email` 实体中增加一个 `attachments` 属性，可以是一个 `List[Attachment]`。
    *   创建一个新的领域对象 `Attachment`，包含 `filename`、`content_type` 和 `content` 等属性。
    *   `Email` 实体可以增加一个新的业务方法，如 `extract_text_from_attachments()`，封装文本提取的核心规则。

    ```python
    # src/email_ingestion/domain/model/email.py (扩展后)
    from dataclasses import dataclass, field
    from typing import List

    @dataclass
    class Attachment:
        filename: str
        content: bytes

    @dataclass
    class Email:
        # ... 其他属性 ...
        attachments: List[Attachment] = field(default_factory=list)

        def get_main_text(self) -> str:
            # 业务逻辑可以变得更丰富
            # 例如，未来可以整合附件文本
            return self.body
    ```

2.  **更新应用服务 (Application Layer)**：
    *   打开 `src/email_ingestion/application/email_service.py`。
    *   修改 `fetch_and_process_emails` 方法，在解析邮件后，同样解析附件并填充到 `Email` 实体中。

    ```python
    # src/email_ingestion/application/email_service.py (扩展后)
    # ...
    class EmailAppService:
        # ...
        def fetch_and_process_emails(self):
            # ...
            for raw_email in raw_emails:
                # ...
                # 解析附件并创建 Attachment 对象
                attachments = self._parse_attachments(parsed)
                email = Email(
                    # ...,
                    attachments=attachments
                )
                self.email_repository.save(email)
    ```

3.  **添加基础设施实现 (Infrastructure Layer)**：
    *   如果需要新的库来处理附件，可以创建一个新的适配器，例如 `src/email_ingestion/infrastructure/attachment_parser.py`。
    *   这个适配器将负责具体的文本提取技术实现，应用服务会调用它，但领域层对此一无所知。
    *   同时，更新 `FileEmailRepository` 的 `save` 方法，使其能够正确地持久化包含附件的 `Email` 对象。

**优势**：
*   **关注点分离**：业务规则的变更（`Email` 现在包含附件）被限制在领域层。技术实现的变更（如何解析PDF）被隔离在基础设施层。流程的变更在应用层。
*   **低耦合**：`knowledge_management` 限界上下文完全不受影响。如果它需要邮件文本，它会通过应用服务接口向 `email_ingestion` 请求，而不是直接依赖其内部实现。
*   **可测试性强**：可以独立测试领域模型的新业务逻辑，也可以独立测试附件解析适配器的功能。
*   **易于维护和理解**：代码的意图非常清晰，新人也能快速理解在哪里添加或修改代码。

通过这个对比，我们可以清晰地看到，DDD 分层架构通过明确的边界和职责划分，极大地提升了系统的可扩展性和可维护性，使得应对未来的需求变化变得更加从容。

### 7.3. 代码量预估对比

现在，我们来估算一下实现这个“邮件附件处理”功能，在两种架构下大致需要编写的代码行数（LOC, Lines of Code）。

*   **旧架构：约 30-40 行**
    *   所有代码将集中修改于 `src/email/email_receiver.py` 这一个文件中。
    *   你需要在 `fetch_emails` 方法内部添加循环、条件判断、调用附件解析库、更新字典等逻辑。
    *   虽然代码行数看起来不多，但这是一种“坏味道”的增长。它将一个已经很复杂的文件变得更加臃肿，增加了维护成本和风险，是一种技术负债的累积。

*   **新架构：约 35-50 行**
    *   **领域层 (`domain/model/email.py`)**: ~10行。定义 `Attachment` 类和在 `Email` 中添加 `attachments` 字段。
    *   **应用层 (`application/email_service.py`)**: ~5-10行。修改应用服务，增加调用附件解析和填充领域对象的逻辑。
    *   **基础设施层 (`infrastructure/attachment_parser.py`)**: ~20-30行。创建一个全新的文件来实现具体的附件文本提取逻辑，封装所有技术细节。

**结论**：

从纯粹的代码行数来看，DDD 架构甚至可能需要编写**更多**的代码。然而，这正是它的优势所在。DDD 架构的“额外”代码都用在了**构建清晰的边界和抽象**上。

-   **旧架构**的 30 行代码是**混乱的、高耦合的**，它们加剧了现有代码的腐化。
-   **新架构**的 40 行代码是**清晰的、高内聚的、低耦合的**，它们被清晰地组织在不同的文件中，每个文件只做一件事。这些代码是健康的、可维护的资产。

因此，DDD 架构的真正价值不在于减少代码的总量，而在于**优化代码的组织结构，提升代码质量和系统的长期健康度**。

## 8. 未来功能扩展对比（二）：跨限界上下文协作

现在我们来看一个更复杂的需求，它要求不同业务模块之间进行协作。

**新需求**：**“需要解析附件中的文档内容，按照知识本体定义提炼出相应的节点和边，并更新到知识图谱中。”**

这个需求横跨了“邮件接收”和“知识管理”两个业务领域，是检验架构设计是否优秀的绝佳案例。

### 8.1. 在旧架构中扩展

在单体结构中，实现这个跨模块功能通常会导致更严重的混乱：

1.  **再次修改 `email_receiver.py`**：你别无选择，只能再次打开这个已经非常臃肿的文件。
2.  **深度耦合**：在 `fetch_emails` 方法中，当处理完附件文本后，你需要直接 `import` `knowledge_graph` 模块，例如 `from ..knowledge_graph.ontology_generator import OntologyGenerator`。
3.  **直接调用**：然后，你需要实例化 `OntologyGenerator` 并调用其方法，例如 `generator.extract_and_update_graph(attachment_text)`。
4.  **混乱的知识边界**：`email` 模块现在必须了解 `knowledge_graph` 模块的内部实现细节，比如它知道有一个叫 `OntologyGenerator` 的类，以及它需要调用哪个方法。如果未来 `OntologyGenerator` 的接口发生变化，`email_receiver.py` 也必须跟着修改。
5.  **事务和错误处理困难**：整个过程（接收邮件、解析附件、提取知识、更新图谱）被强行捆绑在一个方法调用链中。如果最后一步“更新图谱”失败了，如何处理？是回滚整个邮件处理过程，还是忽略这个错误？代码会变得非常复杂且难以维护。

**痛点**：
*   **模块边界被彻底打破**：`email` 模块和 `knowledge_graph` 模块之间形成了紧密的、硬编码的依赖。
*   **职责链过长**：一个类的单一方法横跨了两个完全不同的业务领域。
*   **系统脆弱性增加**：一个模块的内部改动极有可能引发另一个模块的故障。

### 8.2. 在新的 DDD 架构中扩展

在 DDD 架构中，我们通过**领域事件（Domain Events）**来处理跨限界上下文的协作，从而保持模块的独立和解耦。

实现步骤如下：

**1. 在 `email_ingestion` 上下文中发布领域事件**

当 `email_ingestion` 完成了它的本职工作（接收并处理邮件、提取附件文本）后，它会发布一个事件，告知系统的其他部分“有一份新的文本可供分析了”。它不关心谁会监听这个事件，也不关心后续会发生什么。

*   **应用层 (`application/email_service.py`)**

    ```python
    # src/email_ingestion/application/email_service.py (扩展后)
    from ...shared.event_bus import EventBus, AttachmentTextExtracted

    class EmailAppService:
        def __init__(self, email_repository: IEmailRepository, pop3_adapter: POP3Adapter, event_bus: EventBus):
            # ...
            self.event_bus = event_bus

        def fetch_and_process_emails(self):
            # ...
            for raw_email in raw_emails:
                # ... 创建 Email 实体，包含附件文本 ...
                self.email_repository.save(email)

                # 发布领域事件
                event = AttachmentTextExtracted(email_id=email.id, text_content=email.get_main_text())
                self.event_bus.publish(event)
    ```

**2. 在 `knowledge_management` 上下文中订阅并处理事件**

`knowledge_management` 上下文对这个事件感兴趣。它会订阅该事件，并在事件发生时执行自己的业务逻辑。

*   **创建一个新的应用服务 (`application/knowledge_extraction_service.py`)**

    ```python
    # src/knowledge_management/application/knowledge_extraction_service.py
    from ..domain.repository.knowledge_graph_repository import IKnowledgeGraphRepository

    class KnowledgeExtractionService:
        def __init__(self, graph_repository: IKnowledgeGraphRepository):
            self.graph_repository = graph_repository

        def extract_and_save_from_text(self, text: str):
            # 1. 使用领域知识解析文本，生成节点和边
            graph = self.graph_repository.get()
            new_nodes, new_edges = self._perform_extraction(text)
            graph.add_elements(new_nodes, new_edges)
            
            # 2. 使用仓储保存更新后的图谱
            self.graph_repository.save(graph)

        def _perform_extraction(self, text: str):
            # ... 复杂的知识提取逻辑 ...
            pass
    ```

*   **创建事件监听器 (`interfaces/event_listeners.py`)**

    ```python
    # src/knowledge_management/interfaces/event_listeners.py
    from ...shared.event_bus import EventBus
    from ..application.knowledge_extraction_service import KnowledgeExtractionService

    def on_attachment_text_extracted(event):
        # 依赖注入来获取服务实例
        service = get_knowledge_extraction_service()
        service.extract_and_save_from_text(event.text_content)

    def setup_listeners(event_bus: EventBus):
        event_bus.subscribe('AttachmentTextExtracted', on_attachment_text_extracted)
    ```

**优势**：
*   **完全解耦**：`email_ingestion` 和 `knowledge_management` 两个上下文之间没有直接的代码依赖。它们只共享事件的定义。
*   **单一职责**：每个上下文都只关心自己的业务。`email_ingestion` 负责收邮件，`knowledge_management` 负责搞知识。
*   **异步与弹性**：事件驱动的模式天然支持异步处理。如果知识提取失败，可以进行重试，而不会影响邮件接收流程。系统变得更有弹性。
*   **可扩展性**：未来如果有一个新的“情感分析”限界上下文也需要处理邮件文本，它只需要同样订阅 `AttachmentTextExtracted` 事件即可，无需对现有代码做任何修改。

这个案例清晰地展示了 DDD 在处理复杂业务流程时的强大能力，它通过事件驱动机制，将复杂的、跨模块的流程拆解为一系列独立的、高内聚的业务活动，从而保证了整个系统的清晰、健壮和可扩展。

希望这份文档能对您有所帮助！