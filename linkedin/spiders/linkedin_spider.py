import scrapy
import re
import jmespath

class LinkedinSpiderSpider(scrapy.Spider):
    name = "linkedin_spider"
    allowed_domains = ["linkedin.com"]
    # start_urls = ["https://linkedin.com"]

    login_params={
        'session_key':'nischalpoudel0109@gmail.com',
        'session_password':''
    }

    headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

    headers2 = {
        "Connection": "close",
        "sec-ch-ua": "\"Not=A?Brand\";v=\"99\", \"Chromium\";v=\"118\"",
        "x-li-lang": "en_US",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "x-li-page-instance": "urn:li:page:d_flagship3_search_srp_all;",
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": "ajax:5794619676270450000",
        "x-li-track": "{}",
        "x-restli-protocol-version": "2.0.0",
        "x-li-pem-metadata": "Voyager - Search Results Page=search-results",
        "sec-ch-ua-platform": "\"Linux\"",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.linkedin.com/feed/?trk=cold_join_sign_in",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    def start_requests(self):
        yield scrapy.Request("https://www.linkedin.com/uas/login?fromSignIn=true&trk=cold_join_sign_in",callback=self.login_page)

    def login_page(self,response):
        cookies=''
        
        csrftoken=response.css('form[class="login__form"] input[name="csrfToken"]::attr("value")').get()
        sidString=response.css('form[class="login__form"] input[name="sIdString"]::attr("value")').get()
        logincsrfparam=response.css('form[class="login__form"] input[name="loginCsrfParam"]::attr("value")').get()

        cookies_list=response.headers.getlist('Set-Cookie')
        for cookie in cookies_list:
            cookies=cookies+cookie.decode('utf-8').split(';')[0]+'; '

        self.headers['Cookie']=cookie

        self.login_params['csrfToken']=csrftoken
        self.login_params['sIdString']=sidString
        self.login_params['loginCsrfParam']=logincsrfparam

        yield scrapy.FormRequest('https://www.linkedin.com/checkpoint/lg/login-submit',formdata=self.login_params,headers=self.headers,callback=self.login,dont_filter=True,meta={'dont_redirect': True,'handle_httpstatus_list': [301, 302,303]})

    def login(self,response):
        cookies=''
        
        cookies_list=response.headers.getlist('Set-Cookie')
        for cookie in cookies_list:
            ck=cookie.decode('utf-8')
            if 'li_rm=' in ck or 'lang=' in ck or 'JSESSIONID=' in ck or 'bcookie=' in ck or 'bscookie=' in ck or 'li_at=' in ck:
                cookies=cookies+ck.split(';')[0]+'; '
                if 'JSESSIONID=' in ck:
                    self.headers2['csrf-token']=ck.split(';')[0].replace('JSESSIONID="','').replace('"','')
        self.headers2['cookie']=cookies
        
        
        yield scrapy.Request('https://www.linkedin.com/voyager/api/graphql?variables=(start:10,origin:CLUSTER_EXPANSION,query:(keywords:Kiran,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.dec2e0cf0d4c89523266f6e3b44cc87c',callback=self.parse,headers=self.headers2)

    def parse(self, response):
        urls=navigation_urls = re.findall(r'"navigationUrl"\s*:\s*"([^"]+)"', response.text)
        for url in urls:
            uid=re.search(r'/in/([^/?]+)', url).group(1)
            yield scrapy.Request('https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(vanityName:'+uid+')&queryId=voyagerIdentityDashProfiles.fce08d3fe4a26af29aa4182c30b326dc',callback=self.parse_id,headers=self.headers2)

        

    def parse_id(self,response):
        d=response.text
        firstname=re.search(r'"firstName"\s*:\s*"([^"]+)"',d).group(1)
        lastname=re.search(r'"lastName"\s*:\s*"([^"]+)"',d).group(1)
        schoolname=re.search(r'"schoolName"\s*:\s*"([^"]+)"',d).group(1)
        companyname=re.search(r'"companyName"\s*:\s*"([^"]+)"',d).group(1)

        yield {
            'First Name':firstname,
            'last Name':lastname,
            'school name':schoolname,
            'companyname':companyname
        }