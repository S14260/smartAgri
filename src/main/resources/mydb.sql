create table admin
(
    id       int auto_increment
        primary key,
    username varchar(255)  null,
    password varchar(255)  null,
    issuper  int default 0 null,
    sex      varchar(20)   null,
    age      int           null,
    phone    varchar(255)  null
)
    row_format = DYNAMIC;

create table admin_plots
(
    id              bigint auto_increment comment '地块ID'
        primary key,
    name            varchar(100) not null comment '地块名称',
    last_crop       varchar(100) null comment '上季作物',
    current_crop    varchar(100) null comment '本季作物',
    contact_person  varchar(100) null comment '联系人',
    phone           varchar(20)  null comment '电话',
    soil_type       varchar(100) null comment '土壤类型',
    irrigation_type varchar(100) null comment '灌溉条件',
    land_type       varchar(100) null comment '土地类型',
    shape_type      varchar(20)  null comment '图形类型（polygon 或 circle）',
    coordinates     text         null comment '坐标数据（JSON字符串）',
    area            double       null comment '面积（亩）',
    address         varchar(255) null
)
    comment '地块信息表';

create table dormitory
(
    id          int auto_increment
        primary key,
    dormitoryid varchar(255) null,
    floor       int          null,
    bed         int          null,
    price       int          null
)
    row_format = DYNAMIC;

create table punch_record
(
    id         bigint auto_increment
        primary key,
    plot_id    bigint                             null,
    plot_name  varchar(100)                       null,
    longitude  double                             null,
    latitude   double                             null,
    punch_time datetime default CURRENT_TIMESTAMP null,
    user_id    bigint                             null,
    remark     varchar(255)                       null,
    status     int                                null comment '打卡状态：1有效 2无效'
);

create table register
(
    id          int auto_increment
        primary key,
    studentid   varchar(255) null,
    studentname varchar(255) null,
    dormotoryid varchar(255) null,
    grade       varchar(255) null,
    comeout     int          null,
    reason      varchar(255) null,
    runtime     varchar(255) null,
    phone       varchar(255) null,
    isout       int          null
)
    row_format = DYNAMIC;

create table student
(
    id          int auto_increment
        primary key,
    studentid   int         null,
    studentname varchar(20) null,
    sex         varchar(10) null,
    age         int         null,
    department  varchar(20) null,
    grade       varchar(20) null,
    phone       varchar(20) null,
    dormitory   varchar(20) null
)
    row_format = DYNAMIC;

create table user
(
    id       int auto_increment
        primary key,
    username varchar(50)  null,
    password varchar(100) null,
    realname varchar(50)  null,
    sex      varchar(10)  null,
    age      int          null,
    phone    varchar(20)  null,
    constraint username
        unique (username)
);

create table user_plots
(
    id              bigint auto_increment comment '地块ID'
        primary key,
    user_id         bigint                              not null comment '所属用户ID',
    name            varchar(100)                        not null comment '地块名称',
    last_crop       varchar(100)                        null comment '上季作物',
    current_crop    varchar(100)                        null comment '本季作物',
    contact_person  varchar(100)                        null comment '联系人',
    phone           varchar(20)                         null comment '电话',
    soil_type       varchar(100)                        null comment '土壤类型',
    irrigation_type varchar(100)                        null comment '灌溉条件',
    land_type       varchar(100)                        null comment '土地类型',
    shape_type      varchar(20)                         null comment '图形类型（polygon 或 circle）',
    coordinates     text                                null comment '坐标数据（JSON字符串）',
    area            double                              null comment '面积（亩）',
    address         varchar(255)                        null comment '地块地址',
    create_time     timestamp default CURRENT_TIMESTAMP null comment '创建时间',
    update_time     timestamp default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间'
)
    comment '用户地块信息表';

