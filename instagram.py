from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from instagramUserInfo import username, password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys



class Instagram:
    def __init__(self, username, password, account):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'tr,tr_TR'})
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.set_window_size(500, 500)
        self.username = username
        self.password = password
        self.account = account

    def signIn(self):
        self.browser.get("https://www.instagram.com/")
        time.sleep(3)

        usernameInput = self.browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
        passwordInput = self.browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')

        usernameInput.send_keys(self.username)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        time.sleep(3)

    def clearText(self, value):
        if len(value) > 0 and 'Photo by' in value:
            findIndex = value.find('\'')
            findTextCount = len(value)

            newText = ''
            for item in range(findIndex, findTextCount):
                newText += value[item]

            newText = newText.replace(self.account, '')
            newText = newText.replace('@', '')
            newText = newText.removeprefix('\'')
            newText = newText.removesuffix('.')
            newText = newText.removesuffix('\'')
            return newText
        else:
            return ''

    def getPosts(self):
        self.browser.get(f"https://www.instagram.com/{self.account}")
        time.sleep(3)

        try:
            self.browser.find_element_by_css_selector(
                '#react-root > section > main > div > div > article > div > '
                'div > div:nth-child(1) > div:nth-child(1)').click()
            print('success')

        except NoSuchElementException:
            print('error')
            return False

        time.sleep(3)

        posts = {}
        file = open(f"{self.account}.txt", "w", encoding="UTF-8")

        while True:

            try:
                self.browser.find_element_by_xpath('/html/body/div[5]/div[1]/div/div') \
                    .find_element_by_css_selector('a:last-child').click()
                time.sleep(3)

                altValue = self.browser.find_element_by_css_selector(
                    'body > div > div > div > article > div > div > div div img').get_attribute(
                    'alt')

                altKey = str(self.browser.find_element_by_css_selector('body > div > div > div > '
                                                                       'article > div > section > div >'
                                                                       ' div > a').get_attribute('href'))

                postCount = len(posts)
                print(f'count: {postCount}')
                postStatus = True
                if postCount >= 1:
                    for key in list(posts.keys()):
                        if key != altKey:
                            posts[altKey] = altValue
                        else:
                            postStatus = False
                            print('finish...')
                            break
                else:
                    posts[altKey] = altValue

                if postStatus:
                    postText = self.clearText(altValue)
                    print(f'postText clear: {postText}')
                    if len(postText) > 0 and postText != '':
                        print('Eklendi. \n')
                        file.write(postText + "\n")

                if not postStatus:
                    with open(f"json/{self.account}.txt", "w", encoding="UTF-8") as fileJson:
                        fileJson.write(str(posts))

                    # with open(f"{self.account}.txt", "w", encoding="UTF-8") as file:
                    #     for post in posts.values():
                    #         postText = clearText(post)
                    #         if len(postText) > 0 and postText != '':
                    #             file.write(postText + "\n")
                    return

            except NoSuchElementException:
                time.sleep(10)
                print('not found value - sleeping 10 second')


# prices = {'apple': 0.40, 'orange': 0.35, 'banana': 0.25}
# prices['bear'] = 2
# for key in list(prices.keys()):  # Use a list instead of a view
#     if key == 'orange':
#         del prices[key]
# with open("followers.txt", "w", encoding="UTF-8") as file:
#     for item in prices:
#         file.write(item + "\n")

text = "Photo by neonduvarda in İzmir Province with @neonduvarda. May be an image of text that says 'İYİ GECELER BENİ HİÇ YALNIZ BIRAKMAYAN CANIM TAVANIM @neonduvarda'."
# res = text.replace('Photo by neonduvarda in İzmir Province with @neonduvarda. May be an image of text that says \'', '')
if len(text) > 0 and 'Photo bys' in text:
    print('var')
else:
    print('yok')


instgrm = Instagram(username, password, sys.argv[1])
instgrm.signIn()
instgrm.getPosts()
