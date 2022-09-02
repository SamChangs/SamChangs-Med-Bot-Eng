# time_str = '星期一上午看診,星期四上午看診,星期三上午看診,星期一下午看診,星期二下午看診,星期四下午看診,星期一晚間看診,星期二晚間看診,星期三晚間看診'
def str_Format(time_str):
    lin_mark = "**********************************\n"
    str_morning = ""
    str_noon = ""
    str_ning = ""

    arr = time_str.split("、")
    for str in arr:
        if "休診" not in str:
            if "上午" in str:
                str_morning += str[0:3]+","
            if "下午" in str:
                str_noon += str[0:3]+","
            if "晚上" in str:
                str_ning += str[0:3]+","

    def If_none(article):
        if article == "":
            return "No consultation period"
        else:
            return article[0:len(article)-1]

    str_all = '[Morning]\n'+ If_none(str_morning)+'\n' + lin_mark + '[Noon]\n'+ If_none(str_noon)+'\n'  + lin_mark + '[Afternoon]\n'+ If_none(str_ning)+"\n"

    return str_all

