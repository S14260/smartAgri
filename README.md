![image](https://github.com/user-attachments/assets/e54b0079-8a0a-472b-a071-991fd30c699d)# smart-agriculture-management智慧农业管理系统



## 前言

该项目为Java数据库实训课程设计系统，实现简单的curd、分页以及登录

## 项目介绍

`dormitoory-admin`是一个简单的学生宿舍管理系统，基于Springboot+Layui实现。主要实现学生管理、宿舍管理、管理员管理、登记管理等的简单CURD和分页登录功能。

### 项目演示
![image](https://github.com/user-attachments/assets/b925ddf6-b3d4-4569-b085-e83cc3826dbf)


### 技术选型

| 技术       | 说明         | 官网                                             |
| ---------- | ------------ | ------------------------------------------------ |
| Springboot | Java         | https://vuejs.org/                              |
| LayUI      | 前端UI框架   | https://layui.gitee.io/v2/docs/element/anim.html |
| X-admin    | 前端开源项目 | http://x.xuebingsi.com/                          |
| jQuery     | 前端框架     | https://jquery.com/                              |

### 项目布局

```g
main
	└──java
            └── com.dormitooryadmin
	│   │     ├── controller
	│   │	  ├── dao 
	│   │	  ├── model 
	│   │	  └── service 
	│   └── resources
  	│   │	  ├── static 
  	│   │	  └── template
 	└──test   │
   	    └──java
   		  └── com.dormitooryadmin
   			
```



## 后端接口文档

打开网址查看全部接口 https://console-docs.apipost.cn/preview/91636b87fbf569ed/29f529c9f1b40005 密码123456

## 搭建步骤

- 克隆源代码到本地，使用IDEA打开;
- 数据库导入java->resource 下的mydb.sql;
- 在application.yml修改数据库账号密码
- 完成编译;
- 打开 http://localhost:8080/ 默认跳转到登录页面 使用admin admin登录

 
