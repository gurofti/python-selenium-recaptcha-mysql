from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from instagramUserInfo import username, password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys
import mysql.connector


class GittiGidiyor:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="new_password",
            database="py_gittigidiyor"
        )
        self.cursor = self.db.cursor()

        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        time.sleep(3)
        self.page = 1
        self.categoryId = ''
        self.categoryPath = ''
        self.categoryQuery()

    def login(self):
        loginUrl = "https://www.gittigidiyor.com/uye-girisi"
        self.browser.get(loginUrl)
        time.sleep(4)
        self.browser.find_element_by_css_selector('#L-UserNameField').send_keys('xxx@xxxx.com')
        self.browser.find_element_by_css_selector('#L-PasswordField').send_keys('password')
        self.browser.find_element_by_css_selector('#gg-login-enter').click()
        time.sleep(2)
        if loginUrl == self.browser.current_url:
            self.login()
            return
        self.messageSend()

    def productCreate(self, username, path):
        sql = "SELECT * FROM products WHERE path = %s"
        adr = (str(path),)
        self.cursor.execute(sql, adr)
        result = self.cursor.fetchall()
        rowCount = self.cursor.rowcount
        if rowCount < 1:
            sql = "INSERT INTO products (username, path, category_id) VALUES (%s, %s, %s)"
            val = (username, path, self.categoryId)
            self.cursor.execute(sql, val)
            self.db.commit()

    def categoryQuery(self):
        self.cursor.execute("SELECT * FROM categories WHERE status = 0 LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            print('Kategori bulundu.')
            self.categoryId = result[0]
            self.categoryPath = result[1]
            self.page = result[3]
            print(self.categoryId)
            print(self.categoryPath)
        else:
            print('Kategori bulunamadı.')
            self.categoryPath = False
        return

    def categoryUpdate(self, page):
        sql = "UPDATE categories SET status = %s, page = %s WHERE id = %s"
        val = (1, page, self.categoryId)
        self.cursor.execute(sql, val)
        self.db.commit()
        return

    def categoryUrl(self):
        print(f"category url: {self.categoryPath}")
        if self.page == 1:
            return f"https://www.gittigidiyor.com/{self.categoryPath}"
        return f"https://www.gittigidiyor.com/{self.categoryPath}?sf={self.page}"

    def refreshCategory(self):
        time.sleep(10)
        oldPage = self.page
        self.page = 1
        self.categoryUpdate(oldPage)
        self.categoryQuery()
        self.profileData()

    def profileData(self):
        if not self.categoryPath:
            print('Kategoriler işlendi.')
            exit()

        self.browser.get(self.categoryUrl())
        time.sleep(6)

        if self.browser.find_elements_by_css_selector('.catalog-view.products-container '
                                                      '.gg-uw-6.gg-uw-6.gg-w-8 a'):
            try:
                for item in self.browser.find_elements_by_css_selector('.catalog-view.products-container '
                                                                       '.gg-uw-6.gg-uw-6.gg-w-8 a'):
                    self.productCreate('', item.get_attribute('href'))

                if self.browser.find_element_by_css_selector('.pager.pt30.hidden-m.gg-d-24 .next-link'):
                    self.page += 1
                    self.profileData()
                else:
                    print('bulunamadı')

            except NoSuchElementException:
                self.refreshCategory()
        else:
            self.refreshCategory()

    def sellerSave(self, seller):
        sql = "SELECT * FROM users WHERE user_profile = %s"
        adr = (str(seller),)
        self.cursor.execute(sql, adr)
        self.cursor.fetchall()
        rowCount = self.cursor.rowcount
        if rowCount < 1:
            sql = "INSERT INTO users (user_profile) VALUES (%s)"
            val = (seller,)
            self.cursor.execute(sql, val)
            self.db.commit()

    def productVisited(self, productId):
        sql = "UPDATE products SET profile_visit = %s WHERE id = %s"
        val = (1, productId)
        self.cursor.execute(sql, val)
        self.db.commit()

    def profileUserSave(self):
        self.cursor.execute("SELECT * FROM products WHERE profile_visit = 0")
        # self.cursor.execute("SELECT * FROM products WHERE profile_visit = 0 ORDER BY id DESC LIMIT 100")
        result = self.cursor.fetchall()
        if result:
            for product in result:
                self.browser.get(product[2])
                time.sleep(2)
                try:
                    if self.browser.find_element_by_css_selector('#sp-member-href'):
                        seller = self.browser.find_element_by_css_selector('#sp-member-href').get_attribute('href')
                        self.sellerSave(seller)
                        self.productVisited(product[0])
                except NoSuchElementException:
                    self.productVisited(product[0])

            self.profileUserSave()
        else:
            time.sleep(120)
            self.profileUserSave()

    def userMessageSend(self, userId, status):
        sql = "UPDATE users SET send_message = %s WHERE id = %s"
        val = (status, userId)
        self.cursor.execute(sql, val)
        self.db.commit()

    def messageText(self):
        return 'Merhabalar, uğraşıp emek verdiğiniz ürünlerinizi en iyi tanıtabileceğiniz ve bunu çok kısa zaman içerisinde gerçekleştirip müşteri hizmetinize sunabileceğiniz, kendi e-ticaret siteniz için iletişime geçebilirsiniz. Sitenizdeki ürünleri doğrudan pazaryerlerine(çiceksepet, trendyol, hepsi burada, gittigidiyor vs) aktararak hem daha çok kazanç hem de zamandan tasarruf edebilirsiniz. İletişim için 0536-708-1285 whatsapp üzerinden bize ulaşabilirsiniz. Fiyatlarımız 3bin tl den başlamaktadır. İyi kazançlar dileriz. Not: Bu mesaj kendi yazdığımız yazılım botları tarafından atılmaktadır.'

    def messageSend(self):
        self.cursor.execute("SELECT * FROM users WHERE send_message = 0")
        result = self.cursor.fetchall()
        if result:
            for user in result:
                try:
                    self.browser.get(user[1])
                    time.sleep(15)
                    if self.browser.find_element_by_css_selector('#store-page-action-btns > div:nth-child(1) > a'):
                        self.browser.find_element_by_css_selector(
                            '#store-page-action-btns > div:nth-child(1) > a').click()
                        time.sleep(15)
                        self.browser.find_element_by_css_selector('#message').send_keys(self.messageText())
                        time.sleep(15)
                        self.browser.find_element_by_css_selector('.messages-send-container #submit').click()
                        self.userMessageSend(user[0], 1)
                        time.sleep(2)
                except NoSuchElementException:
                    self.userMessageSend(user[0], 2)

            time.sleep(120)
            self.messageSend()
        else:
            time.sleep(120)
            self.messageSend()

class sql:

    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="new_password",
            database="py_gittigidiyor"
        )
        self.cursor = self.db.cursor()

    def query(self):
        sql = "INSERT INTO products (username, path) VALUES (%s, %s)"
        val = ("John", "Highway 21")
        self.cursor.execute(sql, val)
        self.db.commit()

        print(self.cursor.rowcount, "record inserted.")

    def categoryQuery(self):
        self.cursor.execute("SELECT * FROM categories WHERE status = 0 LIMIT 1")
        return self.cursor.fetchone()[0]

    def productCheck(self):
        test = 'aa'
        sql = "SELECT * FROM products WHERE path = %s"
        adr = (
        "https://www.gittigidiyor.com/giyim-aksesuar/kina-taci-sac-orgusu-4-renk-led-isikli-5-li-tt1197_pdp_634748946",)

        self.cursor.execute(sql, adr)
        result = self.cursor.fetchall()
        if result:
            print('bu kayıt daha önceden eklenmiş')
        else:
            print('bulunamadı')


# sqlTest = sql()
# sqlTest.productCheck()
gittiGidiyor = GittiGidiyor()
# gittiGidiyor.profileData()
# gittiGidiyor.profileUserSave()
gittiGidiyor.login()
