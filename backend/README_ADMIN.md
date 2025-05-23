# 管理员用户创建指南

这个文档介绍如何使用 `create_admin.py` 脚本创建管理员用户。

## 安装依赖

在运行脚本之前，请确保已安装所需的依赖：

```bash
# 安装依赖
pip install -r requirements_admin.txt
```

## 创建默认管理员用户

执行以下命令创建默认管理员用户：

```bash
# 进入backend目录
cd backend

# 运行脚本
python create_admin.py
```

默认管理员用户信息：
- 用户名: admin
- 邮箱: admin@example.com
- 密码: admin123

## 创建自定义管理员用户

如果你想创建自定义的管理员用户，可以通过传递参数来实现：

```bash
python create_admin.py <用户名> <邮箱> <密码>
```

例如：

```bash
python create_admin.py superadmin admin@mysite.com securepassword
```

## 重置管理员密码

如果需要重置已存在管理员的密码，可以使用以下命令：

```bash
python create_admin.py --reset-password
```

这将重置默认管理员账户的密码为 `admin123`。

## 注意事项

1. 该脚本直接连接MongoDB数据库，不依赖于Flask应用环境。
2. 确保MongoDB服务器正在运行，并且配置文件中的连接信息正确。
3. 如果指定的邮箱已存在用户，脚本会将该用户设置为管理员，而不是创建新用户。
4. 在生产环境中，请确保使用强密码并在创建后立即更改默认密码。
5. 管理员用户可以访问系统的所有功能，请谨慎授予管理员权限。

## 管理后台访问

创建管理员用户后，可以通过以下URL访问管理后台：

```
http://你的域名/admin/login
```

使用创建的管理员账号和密码登录即可。

## 常见问题排查

1. 如果遇到连接MongoDB的错误，请检查MongoDB服务是否正在运行。
2. 确保config.py文件中的MONGODB_SETTINGS配置正确。
3. 如果遇到导入错误，请确保已安装所有必要的依赖库。