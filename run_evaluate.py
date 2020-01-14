import os
import sys
import glob
import time
import evaluate
import shutil


# target_folder is the folder that contains students' files
target_folder = sys.argv[1]
students_list = glob.glob(os.path.join(target_folder, "*"))
students_list = sorted(students_list)
now_cwd = os.getcwd()

# copy files and execute
# use evaluate.py for each student work directory
for student_path in students_list:
    # be very careful for rmtree!!!
    shutil.rmtree(os.path.join(student_path, "testcase"), ignore_errors=True)
    shutil.rmtree(os.path.join(student_path, "score"), ignore_errors=True)
    shutil.rmtree(os.path.join(student_path, "output"), ignore_errors=True)
    shutil.copytree("testcase", os.path.join(student_path, "testcase"))
    os.chdir(student_path)
    print("Student: " + os.getcwd())
    time.sleep(1)
    evaluate.run_all()

# collect time and cost from each student score.txt
# calculate the score from passing testcase (NO BASELINE RIGHT NOW)
# TODO
time_leaderboard = {}
cost_leaderboard = {}
pass_score = {}
for student_path in students_list:
    student_id = os.path.basename(student_path)
    pass_score[student_id] = 0
    os.chdir(student_path)
    with open(os.path.join("score", "score.txt"), "r") as score_file:
        for s in score_file:
            # parse
            parsed_line = s.split()
            testcase = parsed_line[0]
            time = float(parsed_line[1])
            cost = float(parsed_line[2])
            if time > 0 and cost > 0:
                pass_score[student_id] += 35
            # record
            if testcase not in time_leaderboard:
                time_leaderboard[testcase] = []
                cost_leaderboard[testcase] = []
            time_leaderboard[testcase].append((student_id, time))
            cost_leaderboard[testcase].append((student_id, cost))


# sort function
# make -1 (or any negative value) be the worst place
def sort_func(tup):
    result = tup[1]
    if tup[1] < 0:
        result = sys.maxsize
    return result


# sort time and cost leaderboard
# calculate the points by time and cost leaderboard
for testcase in time_leaderboard:
    item = time_leaderboard[testcase]
    time_leaderboard[testcase] = sorted(
        item, key=sort_func)
for testcase in cost_leaderboard:
    item = cost_leaderboard[testcase]
    cost_leaderboard[testcase] = sorted(
        item, key=sort_func)
time_score = {}
cost_score = {}
for testcase in time_leaderboard:
    time_score[testcase] = []
    cost_score[testcase] = []
    n = len(time_leaderboard[testcase])
    # points
    for i, (student_id, time) in enumerate(time_leaderboard[testcase]):
        if i < n*0.25:
            time_score[testcase].append((student_id, 4))
        elif i < n*0.5:
            time_score[testcase].append((student_id, 3))
        elif i < n*0.75:
            time_score[testcase].append((student_id, 2))
        else:
            time_score[testcase].append((student_id, 1))
    for i, (student_id, cost) in enumerate(cost_leaderboard[testcase]):
        if i < n*0.25:
            cost_score[testcase].append((student_id, 4))
        elif i < n*0.5:
            cost_score[testcase].append((student_id, 3))
        elif i < n*0.75:
            cost_score[testcase].append((student_id, 2))
        else:
            cost_score[testcase].append((student_id, 1))


# find function
# find by student id
def find_by_id(target_id, target_list):
    for (student_id, value) in target_list:
        if student_id == target_id:
            return value


# calculate total points (time_points * cost_points) by each testcase
score = {}
for testcase in time_leaderboard:
    score[testcase] = []
    for i, (student_id, t_point) in enumerate(time_score[testcase]):
        c_point = find_by_id(student_id, cost_score[testcase])
        p = t_point*c_point
        score[testcase].append((student_id, p))


# calculate rank score by each testcase
rank_score = {}
for testcase in score:
    rank_score[testcase] = []
    # rank_file.write("testcase: {}\n".format(testcase))
    item = score[testcase]
    score[testcase] = sorted(item, key=sort_func, reverse=True)
    n = len(score[testcase])
    for i, (student_id, p) in enumerate(score[testcase]):
        if i+1 < n*0.25:
            rank_score[testcase].append((student_id, 15))
        elif i+1 < n*0.5:
            rank_score[testcase].append((student_id, 10))
        elif i+1 < n*0.75:
            rank_score[testcase].append((student_id, 5))
        else:
            rank_score[testcase].append((student_id, 0))


# output final score
os.chdir(now_cwd)
with open("rank.txt", "w") as rank_file:
    for student_path in students_list:
        student_id = os.path.basename(student_path)
        s = pass_score[student_id]
        for testcase in rank_score:
            r = find_by_id(student_id, rank_score[testcase])
            if r is not None:
                s += r
        rank_file.write("{} {}\n".format(student_id, float(s)/5.))
