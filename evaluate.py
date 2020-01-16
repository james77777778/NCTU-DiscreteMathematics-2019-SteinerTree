import os
import sys
import time
import glob
import math
import logging
import platform
import subprocess
import networkx as nx


TIMEOUT = 20
OUTPUT = "output"
SCORE = "score"
# For Linux and maybe MacOS
file_suffix = ""
command_prefix = "./"
exec_program_shell = False
# For Windows
if platform.system() == "Windows":
    file_suffix = ".exe"
    command_prefix = ""
    exec_program_shell = True


def validate_classical(output, testcase):
    G = nx.Graph()
    terminals = []
    out_G = nx.Graph()
    res = {
        "contains_all_t": True,
        "is_tree": True,
        "is_connected": True,
        "is_subgraph": True,
        "cost": -1}
    with open(testcase, 'r') as lines:
        for line in lines:
            parsed_line = line.split()
            a = int(parsed_line[0])
            b = int(parsed_line[1])
            w = float(parsed_line[2])
            G.add_edge(a, b, weight=w)
    with open(testcase+".terminals", 'r') as lines:
        for line in lines:
            parsed_line = line.split()
            t = int(parsed_line[0])
            terminals.append(t)
    try:
        with open(output, 'r') as lines:
            for line in lines:
                parsed_line = line.split()
                a = int(parsed_line[0])
                b = int(parsed_line[1])
                # w = float(parsed_line[2])
                out_G.add_edge(a, b)
    except FileNotFoundError:
        logging.error("No such file: {}".format(output))
        res["no_such_file"] = True
        return res
    # check terminals
    for t in terminals:
        if t not in out_G:
            res["contains_all_t"] = False
            break
    try:
        # check if out_G is connected
        res["is_connected"] = nx.is_connected(out_G)
        # check if out_G is tree
        res["is_tree"] = nx.is_tree(out_G)
    except nx.exception.NetworkXPointlessConcept:
        logging.error("Null graph: {}".format(output))
        res["no_such_file"] = True
        return res
    # check all nodes and edges
    for n in list(out_G.nodes()):
        if not G.has_node(n):
            res["is_subgraph"] = False
            break
    for e1, e2 in list(out_G.edges()):
        if not G.has_edge(e1, e2):
            res["is_subgraph"] = False
            break
    res["cost"] = 0
    for e1, e2 in out_G.edges():
        try:
            res["cost"] += G[e1][e2]["weight"]
        except KeyError:
            print("Error Edge: {} {}".format(e1, e2))
            res["cost"] = -1
            break
    return res


def validate_euclidean(output, testcase):
    G = nx.Graph()
    terminals = []
    res = {
        "contains_all_t": True,
        "is_tree": True,
        "is_connected": True,
        "is_subgraph": True,
        "cost": -1}

    nodes = []
    terminals = []
    with open(testcase, 'r') as lines:  # terminals coordinates
        for i, line in enumerate(lines):
            if i == 0:
                continue
            parsed_line = line.split()
            if parsed_line[0] == '':
                del parsed_line[0]
            if parsed_line[-1] == '':
                del parsed_line[-1]
            x = float(parsed_line[0])
            y = float(parsed_line[1])
            z = float(parsed_line[2])
            nodes.append([x, y, z])
            terminals.append(i)
            G.add_node(i)
    try:
        with open(output, 'r') as lines:
            for line in lines:
                if len(line.split(',')) > 1:  # end steiner node
                    edges = line.strip('\n').split(',').copy()
                    break
                parsed_line = line.split()
                try:
                    x = float(parsed_line[0])
                    y = float(parsed_line[1])
                    z = float(parsed_line[2])
                    nodes.append([x, y, z])
                    G.add_node(i)
                except IndexError:
                    logging.error("Fail to parse: {}".format(output))
                    res["no_such_file"] = True
                    return res
            if edges[0] == '':
                del edges[0]
            if edges[-1] == '':
                del edges[-1]
            for edge in edges:
                n1 = int(edge.split('-')[0])
                n2 = int(edge.split('-')[1])
                distance = math.sqrt(
                    (nodes[n1-1][0]-nodes[n2-1][0])**2 +
                    (nodes[n1-1][1]-nodes[n2-1][1])**2 +
                    (nodes[n1-1][2]-nodes[n2-1][2])**2)
                G.add_edge(n1, n2, weight=distance)
    except (FileNotFoundError, UnboundLocalError):
        logging.error("No such file: {}".format(output))
        res["no_such_file"] = True
        return res

    for t in terminals:
        if t not in G:
            res["contains_all_t"] = False
            break
    # check if out_G is connected
    res["is_connected"] = nx.is_connected(G)
    # check if out_G is tree
    res["is_tree"] = nx.is_tree(G)
    # check all nodes and edges
    for n in list(G.nodes()):
        if not G.has_node(n):
            res["is_subgraph"] = False
            break
    res["cost"] = G.size(weight="weight")
    return res


def exec_program(args):
    p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        shell=exec_program_shell)
    try:
        ts = time.perf_counter()
        stdouts, stderrs = p.communicate(timeout=TIMEOUT)
        te = time.perf_counter() - ts
    except subprocess.TimeoutExpired:
        te = time.perf_counter() - ts
        logging.info("Timeout")
        stdouts = ""
    if len(stdouts) > 0:
        logging.info(stdouts.decode("utf-8"))
    return te


def score(score_file, res, testcase_name):
    if "no_such_file" in res:
        score_file.write("{} {} {}\n".format(
            testcase_name, -1.0, -1.0))
        return
    fail = False
    if not res["contains_all_t"]:
        logging.error("Output lacks some terminals")
        fail = True
    if not res["is_tree"]:
        logging.error("Output is not a tree")
        fail = True
    if not res["is_connected"]:
        logging.error("Output is not connected")
        fail = True
    if not res["is_subgraph"]:
        logging.error("Output is not a subgraph of input graph")
        fail = True
    if not fail:
        logging.info(
            "Time: {:>8.5f}   Cost: {:>8.1f}".format(
                round(res["time"], 5),
                res["cost"])
        )
        score_file.write("{} {} {}\n".format(
            testcase_name, res["time"], res["cost"]))
    else:
        logging.info(
            "{}: Time: {:>8.5f}   Cost: {:>8.1f}".format(
                testcase_name, -1.0, -1.0)
        )
        score_file.write("{} {} {}\n".format(
            testcase_name, -1.0, -1.0))


def run_all():
    # Init working dir
    os.makedirs(OUTPUT, exist_ok=True)
    os.makedirs(SCORE, exist_ok=True)

    # Init evaluation parameters
    score_file = open(os.path.join(SCORE, "score.txt"), "w")
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler("evaluation.log", mode='w'),
                            logging.StreamHandler(sys.stdout)])
    logging.info(os.getcwd())
    # Find necessary files
    exec_list = glob.glob("*")
    classical_testlist = glob.glob(
        os.path.join("testcase", "classical", "*.stp"))
    euclidean_testlist = glob.glob(
        os.path.join("testcase", "euclidean", "*.stp"))
    classical_testlist = sorted(classical_testlist)
    euclidean_testlist = sorted(euclidean_testlist)

    # Makefile
    if "Makefile" in exec_list:
        p = subprocess.run(
            'make', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info(p.stdout.decode("utf-8"))

    # Classic Steiner Tree
    exec_list = glob.glob("*")
    is_classic_c = "classical{}".format(file_suffix) in exec_list
    is_classic_py = "classical.py" in exec_list

    if is_classic_c:
        for testcase in classical_testlist:
            testcase_name = os.path.basename(testcase)
            logging.info("{} STARTS".format(testcase_name))
            args = ["{}classical".format(command_prefix),
                    testcase,
                    testcase+".terminals"]
            te = exec_program(args)
            out = os.path.join(OUTPUT, testcase_name+".outputs")
            res = validate_classical(out, testcase)
            res["time"] = te
            score(score_file, res, testcase_name)

    if is_classic_py and not is_classic_c:
        for testcase in classical_testlist:
            testcase_name = os.path.basename(testcase)
            logging.info("{} STARTS".format(testcase_name))
            args = ["python3", "classical.py", testcase, testcase+".terminals"]
            te = exec_program(args)
            out = os.path.join(OUTPUT, testcase_name+".outputs")
            res = validate_classical(out, testcase)
            res["time"] = te
            score(score_file, res, testcase_name)

    # Euclidean Steiner Tree
    is_euclidean_c = "euclidean{}".format(file_suffix) in exec_list
    is_euclidean_py = "euclidean.py" in exec_list

    if is_euclidean_c:
        for testcase in euclidean_testlist:
            testcase_name = os.path.basename(testcase)
            logging.info("{} STARTS".format(testcase_name))
            args = ["{}euclidean".format(command_prefix),
                    testcase]
            te = exec_program(args)
            out = os.path.join(OUTPUT, testcase_name+".outputs")
            res = validate_euclidean(out, testcase)
            res["time"] = te
            score(score_file, res, testcase_name)

    if is_euclidean_py and not is_euclidean_c:
        for testcase in euclidean_testlist:
            testcase_name = os.path.basename(testcase)
            logging.info("{} STARTS".format(testcase_name))
            args = ["python3", "euclidean.py", testcase]
            te = exec_program(args)
            out = os.path.join(OUTPUT, testcase_name+".outputs")
            res = validate_euclidean(out, testcase)
            res["time"] = te
            score(score_file, res, testcase_name)

    score_file.close()
    # logging.shutdown()


if __name__ == "__main__":
    run_all()
