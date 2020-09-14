var vm = new Vue({
    el: '#app',
    data: {
        host,
        error_username: false,
        error_pwd: false,
        error_pwd_message: '请填写密码',
        username: '',
        password: '',
        remember: false
    },
    methods: {
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        // 检查数据
        check_username: function(){
            this.error_username = !this.username;
        },
        check_pwd: function(){
            if (!this.password) {
                this.error_pwd_message = '请填写密码';
                this.error_pwd = true;
            } else {
                this.error_pwd = false;
            }
        },
        // 表单提交
        on_submit: function(){
            this.check_username();
            this.check_pwd();

            if (this.error_username === false && this.error_pwd === false) {
                axios.post(this.host + '/authorizations/', {
                        username: this.username,
                        password: this.password
                    }, {
                        responseType: 'json',
                        withCredentials: true
                    })
                    .then(response => {
                        // 使用浏览器本地存储保存token
                        if (this.remember) {
                            // 勾选了记住登录
                            sessionStorage.clear();
                            localStorage.token = response.data.token;
                            localStorage.user_id = response.data.user_id;
                            localStorage.username = response.data.username;
                        } else {
                            // 未勾选记住登录而成功登陆，需要把之前记住登陆的用户记录都清除掉
                            localStorage.clear();
                            sessionStorage.token = response.data.token;
                            sessionStorage.user_id = response.data.user_id;
                            sessionStorage.username = response.data.username;
                        }

                        // 跳转到登陆前的页面
                        // 凡是跳转到登陆页面的，在路径上添上 next 参数，登陆成功后可以回跳
                        var return_url = this.get_query_string('next');
                        if (!return_url) {
                            return_url = '/index.html';
                        }
                        // location.href 当前页面跳转至新的 URL 页面，?next=/index.html
                        location.href = return_url;
                    })
                    .catch(error => {
                        this.error_pwd_message = '用户名或密码错误';
                        this.error_pwd = true;
                    })
            }
        },
         // qq登录
        qq_login: function(){
            var state = this.get_query_string('next') || '/';
            // 从 URL 获取 next 参数
            axios.get(this.host + '/oauth/qq/authorization/?state=' + state, {
                    responseType: 'json'
                })
                .then(response => {
                    // 引导用户跳转到qq登录页面
                    // 后端 return Response({"oauth_url": login_url})

                    // self.location.href="url"      仅在本页面打开url
                    // window.location.href="url"    当前页面打开URL页面
                    // this.location.href="url"      用法和self.location.href一样
                    // location.href="url"           当前页面打开URL页面
                    // parent.location.href="url"    在父窗口打开此url窗口
                    // top.location.href="url"       在顶层页面打开url（跳出框架）
                    location.href = response.data.oauth_url;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
    }
});
