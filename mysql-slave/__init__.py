"""
docker pull mysql
docker run --name mysql -p 8306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql

docker run  // 启动容器
--name mysql  // 指定容器名称为 mysql
-e MYSQL_ROOT_PASSWORD=root  // 配置环境变量，指定 root 用户的密码为 root
-d  // 是否后台启动，默认false
-p 8306:3306  // 将 3306 端口映射出来为8306进行访问
mysql  // 镜像名称

测试连接
mysql -uroot -proot -h127.0.0.1 --port=8306
mysql> show databases;

先来进行冷备份
mysqldump -uroot -proot --all-databases --lock-all-tables > d:/pycharm/master_db.sql
使用左箭头往 docker 的 mysql 进行导入
mysql -uroot -proot -h127.0.0.1 --port=8306 < d:/pycharm/master_db.sql

设置主从
找到主数据库的配置文件 my.cnf(或者my.ini)，一般在 mysql 目录下
在[mysqld]部分插入如下两行：
[mysqld]
log-bin=mysql-bin  # 开启二进制日志
server-id=1  # 设置server-id

登入主服务器 MySQL 创建从服务器的同步账号
mysql> CREATE USER 'slave'@'%' IDENTIFIED BY 'slave';
mysql> GRANT REPLICATION SLAVE ON *.* TO 'slave'@'%';
mysql> flush privileges;
*.* 表示主服务器的所有数据库都可以访问，@'%'表示所有 ip 地址登陆的从服务器均可访问

获取二进制记录信息，记录二进制文件名(binlog.xxx)和位置(xxx)   000016 |     1138
mysql> SHOW MASTER STATUS;

进入 docker 中的 MySQL 配置从服务器
mysql -uroot -proot -h127.0.0.1 --port=8306

从容器内拷贝文件到主机上
docker cp <containerId>:/<file-path-within-container> <host-path-target>/
docker container ls
docker cp b80f32b4490b:/etc/mysql/my.cnf d:/pycharm/
在[mysqld]后面任意一行添加“skip-grant-tables”用来跳过密码验证的过程
从主机上拷贝文件到容器内
docker cp d:/pycharm/my.cnf b80f32b4490b:/etc/mysql/

mysql> alter user 'root'@'localhost' identified by 'root';
mysql> use mysql；
mysql> update user set host = "%" where user = "root";
mysql> flush privileges;
mysql> select User,authentication_string,Host from user;
mysql> quit

从服务器slave修改，在 my.cnf 配置文件，添加 server-id
[mysqld]
server-id=2  # 设置server-id，必须唯一
binlog-ignore-db = mysql

mysql> CHANGE MASTER TO MASTER_HOST='172.20.80.1', MASTER_USER='slave', MASTER_PASSWORD='slave',
        MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=156 ,get_master_public_key=1;
注意 ip 地址必须从主机的网络连接状态中获取
mysql> start slave;
mysql> STOP SLAVE IO_THREAD FOR CHANNEL;
mysql> show slave status \G
当 Slave_IO_Running 和 Slave_SQL_Running 都为 YES 的时候就表示主从同步设置成功了

错误原因：密码加密方式不支持，在主服务器执行以下命令：
ALTER USER ‘slave’@’%’ IDENTIFIED WITH mysql_native_password BY ‘slave’;
FLUSH PRIVILEGES;

检查
mysql> show variables like 'server_id';

#全局锁表操作
mysql> Flush tables with read lock;
记录下  mysql-bin.000001 |      156

select uuid() as uuid;
D:\Program Files\mysql\data\auto.cnf
net stop mysql
net start mysql

docker 查询 主机 ip
apt-get update
apt-get install net-tools
apt-get install iputils-ping
Unable to locate package错误： apt-get update

docker cp b80f32b4490b:/var/lib/mysql/auto.cnf d:/pycharm/
mysql> unlock tables;

测试
mysql> create database test0914 default charset=utf8;


"""

