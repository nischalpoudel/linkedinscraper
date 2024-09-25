import scrapy
import re

class LinkedinSpiderSpider(scrapy.Spider):
    name = "linkedin_spider"
    allowed_domains = ["linkedin.com"]
    # start_urls = ["https://linkedin.com"]

    login_params={
        'session_key':'xorohi1071@exweme.com',
        'session_password':'DIPdip123'
    }

    headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

    def start_requests(self):
        yield scrapy.Request("https://www.linkedin.com/uas/login?fromSignIn=true&trk=cold_join_sign_in",callback=self.login_page)

    def login_page(self,response):
        cookies=''
        
        csrftoken=response.css('form[class="login__form"] input[name="csrfToken"]::attr("value")').get()
        sidString=response.css('form[class="login__form"] input[name="sIdString"]::attr("value")').get()
        logincsrfparam=response.css('form[class="login__form"] input[name="loginCsrfParam"]::attr("value")').get()

        cookies_list=response.headers.getlist('Set-Cookie')
        for cookie in cookies_list:
            print("Cookie:", cookie.decode('utf-8').split(';')[0])
            cookies=cookies+cookie.decode('utf-8').split(';')[0]+'; '

        self.headers['Cookie']=cookie

        self.login_params['csrfToken']=csrftoken
        self.login_params['sIdString']=sidString
        self.login_params['loginCsrfParam']=logincsrfparam

        yield scrapy.FormRequest('https://www.linkedin.com/checkpoint/lg/login-submit',formdata=self.login_params,headers=self.headers,callback=self.login)

    def login(self,response):
        print()
        print()
        print()
        print('response status:')
        print(response.status)
        print('response headers:')
        print(response.headers)
        print()
        print()
        print()

    def parse(self, response):
        pass
