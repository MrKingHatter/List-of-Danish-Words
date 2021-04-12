import requests
from bs4 import BeautifulSoup

web_page = 'https://ordnet.dk/ddo/ordbog?query=a'  # Some starting point


def soup_link(link, parser='html.parser'):
    return BeautifulSoup(requests.get(link).content, parser)


def fetch_words(lnk):
    soup = soup_link(lnk)  # Formats page
    alpha_list = soup.find('dl', attrs={'id': 'alpha-panel'})  # Find the panel with words
    words = alpha_list.find('div', attrs={'class': 'searchResultBox'}).findAll('a')  # Find the links in the panel
    save_word(words)  # Pass the list of words to save_word()
    return soup.find('div', attrs={'class': 'rulNed'}).find('a')['href']  # Return the link for next page


def save_word(word_list):
    global complete_list
    for word in word_list:
        for child in word.findAll('span'):
            child.decompose()  # Remove clutter from word (super- and lower scripts etc.)
        word = word.text.replace('\t', '').replace('\n', '').strip().split('  ')  # Format words
        for t_word in word:
            if t_word.isalpha():  # Filter words that contains non alphabetical symbols
                complete_list.append(t_word.lower())  # Save the word to the list


complete_list = []
n, starting_interval = 0, []
run = True
while run:
    web_page = fetch_words(web_page)

    # Find the id's of the words currently visible
    temp = [int(''.join([integer for integer in sub if integer.isdigit()]))
            for sub in web_page[web_page.find('browse=down&') + len('browse=down&') + 1:
                                min(web_page.find('&select='), web_page.find('&query='))].split('&')]
    print(f'\rSearch number: {n}, {temp}', end='')

    # Check if you are back to the starting point
    if not starting_interval:
        starting_interval = [x for x in range(temp[1],  temp[0] + 1)]
    else:
        if (temp[0] in starting_interval) | (temp[1] in starting_interval):
            run = False
    n += 1

print('\nReading completed. ', end='')
complete_list = list(dict.fromkeys(complete_list))  # Remove duplicates
print(f'Words found: {len(complete_list)}')

file = open('WordBankDanish.txt', 'w')
complete_list = '\n&'.join(complete_list).split('&')  # Add newlines between the words
file.writelines(complete_list)  # Save the list as a .txt
file.close()
print(f'\nSuccessfully saved the list!')
