import os
import sys
import glob


# target_folder is the folder that contains students' files
final_folder = sys.argv[1]
makeup_folder = sys.argv[2]
# final_folder = "/home/hongyu/workplace/dm/final_check/"
# makeup_folder = "/home/hongyu/workplace/dm/test/"
final_list = glob.glob(os.path.join(final_folder, "*"))
final_list = sorted(final_list)
makeup_list = glob.glob(os.path.join(makeup_folder, "*"))
makeup_list = sorted(makeup_list)
now_cwd = os.getcwd()


def is_scored_before(final_score_list, check_testcase):
    for one_final_score in final_score_list:
        testcase, time, cost = one_final_score.split(" ")
        if check_testcase == testcase:
            if time != "-1.0":
                return True
            if cost != "-1.0":
                return True
    return False


makeup_score = {}
# copy files and execute
# use evaluate.py for each student work directory
for makeup_path in makeup_list:
    fianl_string = ""
    makeup_string = ""
    student_id = os.path.basename(makeup_path)
    if student_id not in makeup_score:
        makeup_score[student_id] = 0
    final_score_path = os.path.join(
        final_folder, student_id, "score", "score.txt")
    makeup_score_path = os.path.join(
        makeup_path, "score", "score.txt"
    )
    try:
        with open(final_score_path, 'r') as final_score_file:
            fianl_string = final_score_file.read()
    except OSError:
        fianl_string = ""
    try:
        with open(makeup_score_path, 'r') as makeup_score_file:
            makeup_string = makeup_score_file.read()
    except OSError:
        makeup_string = ""

    if fianl_string[-1] == "\n":
        fianl_string = fianl_string[:-1]
    if makeup_string[-1] == "\n":
        makeup_string = makeup_string[:-1]
    final_score_list = fianl_string.split("\n")
    makeup_score_list = makeup_string.split("\n")
    for one_makeup_score in makeup_score_list:
        testcase = one_makeup_score.split(" ")[0]
        if "-1" in one_makeup_score:
            continue
        if not is_scored_before(final_score_list, testcase):
            makeup_score[student_id] += 35

with open("makeup_score.txt", "w") as rank_file:
    for makeup_path in makeup_list:
        student_id = os.path.basename(makeup_path)
        s = makeup_score[student_id]
        rank_file.write("{} {}\n".format(student_id, float(s)/5.*0.9))
