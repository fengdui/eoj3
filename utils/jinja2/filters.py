import re

from django_jinja import library
from submission.models import STATUS_CHOICE
import utils.markdown3 as md3
from bs4 import BeautifulSoup
from utils.xss_filter import XssHtml


@library.filter(name='status_choice')
def status_choice(value):
    return dict(STATUS_CHOICE).get(value)


@library.filter(name='timedelta')
def timedelta_format(value):
    days, seconds = value.days, value.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if days == 0:
        return "{}:{:02}".format(hours, minutes)
    else:
        return "{}:{:02}:{:02}".format(days, hours, minutes)


@library.filter(name="minute_filter")
def minute_format(seconds):
    return "%d:%.2d:%.2d" % (seconds // 3600,
                             seconds % 3600 // 60,
                             seconds % 60)


@library.filter(name='markdown')
def markdown_format(value):
    return md3.convert(value)


@library.filter(name='sample')
def sample_format(value):
    """
    :param value: use \n---(or more)\n to split samples, use \ to indicate this line will be a raw line
    :return: html
    """
    def strip_and_remove_slash(text):
        def remove_slash_at_the_beginning(text):
            if text.startswith('\\'):
                text = text[1:]
            return text
        text = text.strip()
        return '\n'.join(map(remove_slash_at_the_beginning, text.strip().split('\n')))

    lst = list(filter(lambda x: x, map(strip_and_remove_slash, re.split(r'(\r?\n)(?<!\\)-+(\1)', value))))
    template = """
    <div class="example">
      <div class="input">
        <div class="title">Input</div>
        <pre>{input}</pre>
      </div>
      <div class="output">
        <div class="title">Output</div>
        <pre>{output}</pre>
      </div>
    </div>
    """
    res = ''
    for i in range(0, len(lst), 2):
        if i + 1 < len(lst):
            res += template.format(input=lst[i], output=lst[i+1])
    return res


@library.filter(name='get_intro')
def get_intro(value):
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(' ')[:256]


@library.filter(name='n2br')
def n2br(value):
    return value.replace('\n', "<br>")


@library.filter(name="safer")
def xss_filter(value):
    parser = XssHtml()
    parser.feed(str(value))
    parser.close()
    return parser.getHtml()
