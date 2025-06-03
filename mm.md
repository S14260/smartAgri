graph TD
    %% 前端层
    A[农户端Web/H5] -->|录入生产数据| B(中间服务层)
    C[物流端App] -->|更新运输信息| B
    D[质检机构PC端] -->|上传检测报告| B
    E[消费者扫码] -->|查询溯源| B
    F[监管平台] -->|审计追踪| B

    %% 中间服务层
    B --> G[数据上链模块]
    B --> H[签名验证模块]
    B --> I[IPFS接口模块]
    B --> J[数据解析模块]

    %% 智能合约层
    G --> K[以太坊智能合约]
    H --> K
    I --> K
    K -->|存储哈希| L[以太坊区块链]
    K -->|记录CID| M[IPFS存储]

    %% 存储层
    M -->|图片/视频/PDF| N[IPFS节点1]
    M -->|传感器数据| O[IPFS节点2]
    M -->|检测报告| P[IPFS节点3]

    %% 图例说明
    style A fill:#F9E79F,stroke:#333
    style C fill:#AED6F1,stroke:#333
    style D fill:#A2D9CE,stroke:#333
    style E fill:#F5B7B1,stroke:#333
    style F fill:#D2B4DE,stroke:#333
    style B fill:#E5E7E9,stroke:#333,stroke-width:2px
    style K fill:#F1948A,stroke:#333
    style L fill:#BB8FCE,stroke:#333
    style M fill:#85C1E9,stroke:#333
