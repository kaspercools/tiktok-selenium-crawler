import os.path
import uuid
import shutil
from os import path
from selenium.webdriver.common.action_chains import ActionChains
import time
import io
from time import sleep
import DataReader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# setup the chrome webdriver
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 0)


def scroll_to_bottom(element):
    # left in here but does nothing (for now)

    driver.execute_script('arguments[0].scrollIntoView(true);', element)


def navigate_to_video(authorHandle, videoId):
    print('move browser')
    print("https://www.tiktok.com/@" + authorHandle + "/video/" + videoId+'?enter_from=video_detail&is_copy_url=1&is_from_webapp=v1')
    driver.get("https://www.tiktok.com/@" + authorHandle + "/video/" + videoId+'?enter_from=video_detail&is_copy_url=1&is_from_webapp=v1')
    
    print('now get element')
    comment_container = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]')))#
        #'/html/body/div[2]/div[2]/div[3]/div[2]/div[3]')))
    print('scroll to bottom')


def process_posts(data):
    newPosts = []
    if 'top_videos' in data:
        for post in data['top_videos']:
            try:
                updatedPost = process_individual_post(post)
                currentPath = path.join(resultsPath, data['title'], str(uuid.uuid4())+'.json')
                print(resultsPath + '/' + data['title'] + '/' + str(uuid.uuid4()))
                updatedPost['keyword'] = data['title']
                DataReader.write_json_to_file(updatedPost, currentPath)

            except Exception as e:
                print(e)


    return newPosts


def process_individual_post(post):
    print('navigate')
    navigate_to_video(post['username'], post['id'])
    comments = get_comments()
    reveal_nested_comments(comments)
    print('scaffold')
    comments = scaffold_comments2()

    post['comments'] = comments;
    return post


def scaffold_comments2():
    comments = []
    comment_containers = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]/div')#'/html/body/div[2]/div[2]/div[3]/div[2]/div[3]/div')
    for container in comment_containers:
        comments.append(build_comment2(container))
    return comments


def scaffold_comments():
    comments = []
    print('get scaffolded items')
    comment_containers = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[2]/div[3]/div')
    for container in comment_containers:
        comments.append(build_comment(container))

    return comments


def build_comment2(container):
    print('build comment2 \n\n')
    subContainers = container.find_elements(By.XPATH, './child::*')

    if len(subContainers) > 0:
        print('get first div')
        comment = extract_comment(subContainers[0])

    if len(subContainers) > 1:
        # todo loop through subs
        print('hypothetical loop')
        comment['replies'] = []
        for nestedContainer in subContainers[1].find_elements(By.XPATH, ('./div')):
            currentComment = extract_comment(nestedContainer);
            if not currentComment is None:
                comment['replies'].append(currentComment)

    return comment


def extract_comment(commentContainer):
    exists = len(commentContainer.find_elements(By.XPATH, ('./a'))) > 0
    if not exists: return None
    comment = {}
    userUrl = commentContainer.find_element(By.XPATH, ('./a')).get_attribute('href')
    userName = commentContainer.find_element(By.XPATH, ('./div/a/span')).text
    userComment = commentContainer.find_element(By.XPATH, ('./div/p[1]/span')).text
    comment = {
        'usr_uri': userUrl,
        'name': userName,
        'comment': userComment
    }
    return comment


def build_comment(parentCommentChildren):
    comment = {}
    try:

        driver.implicitly_wait(0)
        exists = len(parentCommentChildren.find_elements(By.XPATH, ("./div/a"))) > 0

        driver.implicitly_wait(4)

        if exists:
            userUrl = parentCommentChildren.find_element(By.XPATH, ('./div/a')).get_attribute('href')
            userName = parentCommentChildren.find_element(By.XPATH, ('./div/div/a/span')).text
            userComment = parentCommentChildren.find_element(By.XPATH, ('./div[1]/div/p[1]/span')).text
            comment = {
                'usr_uri': userUrl,
                'name': userName,
                'comment': userComment
            }


    except Exception as e:
        print("not a printable comment?")
        print(e)
        exit()

    try:
        containers = parentCommentChildren.find_elements(By.XPATH, ("./child::*"))[1:]
        comment['replies'] = []
        for container in containers:
            # print(comment)
            print('jumping in container..')
            additionalComments = build_comment(container)
            if len(additionalComments) > 0:
                comment['replies'].append(additionalComments)

    except:
        print('cant find children')

    # print(comment)
    return comment


def reveal_nested_comments(comments):
    print('reveal nested comments')
    appendix = ""
    for i in range(0, 1):
        # print(str(i))
        for comment in comments:
            pTags = comment.find_elements(By.XPATH,
                                          ("//p[contains(concat(' ', @data-e2e, ' '), 'view-more" + appendix + "')]"))
            for tag in pTags:
                try:
                    tag2 = wait.until(EC.element_to_be_clickable(tag))
                    tag2.click()
                except Exception as e:
                    print(format(e))
        if i == 1:
            appendix = '-' + (str(i + 1))

    print('done clicking')


def find_nested_comments(element):
    userUrl = ""
    userComment = ""
    a = element.find_elements(By.XPATH, ('./a'))
    els = element.find_elements(By.XPATH, ('./*'))

    for el in els:
        if (el.tag_name == "a"):
            userUrl = el.get_attribute('href')
        elif (el.tag_name == "span"):
            userComment = el.text

        # userName = el.find_element(By.XPATH,('./a/span')).text
        # userComment = el.find_element(By.XPATH,('./p/span')).text
        print(el.get_attribute('innerHTML'))


def get_comments():
    driver.implicitly_wait(5)
    comments = driver.find_elements(By.XPATH, ('//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]/div'))
    return comments


def process_comments(comments):
    comment_results = []
    print('print comments')
    print(comments)
    reveal_nested_comments(comments)
    print(comments)
    for comment in comments:
        userUrl = comment.find_element(By.XPATH, ('/div[1]/div[1]/a')).get_attribute('href')
        userName = comment.find_element(By.XPATH, ('/div[1]/div[1]/a/span')).text
        userComment = comment.find_element(By.XPATH, ('/div[1]/div[1]/p/span')).text

        comment_results.append({
            'usr_uri': userUrl,
            'name': userName,
            'comment': userComment
        })

        print({
            'usr_uri': userUrl,
            'name': userName,
            'comment': userComment
        })

    find_nested_comments(comment.find_element(By.XPATH, ('/div[1]/div[2]')))
    return comment_results


# collect data from comments

# for eacht comment go to page 
# open post
# read comments
# save comments to file
todoPath = "./todo"
skippedPath = "./skipped"
resultsPath = "./results"
processedPath="./processed"
pendingPath = "./pending"
failedPath = "./failed"
print('running script')

while(True):
    toBeProcessed = DataReader.get_files(todoPath + '/tmp.json')

    for file in toBeProcessed:
        posts = DataReader.read_json(file)
        # posts contains posts to be processed
        # process postsprint
        # process postsprint
        for post in posts:
            process_posts(post)
        
        shutil.move(file, path.join(processedPath, post['title'], post['id']+'.rand.json'))
