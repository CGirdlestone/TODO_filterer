"""todo.py A CLI program to allow filtering and displaying a todo list.

This script allows the user to filter and display a todo list by various
parameters. It is assumed that the user's todo list follows the format outlined
in https://github.com/todotxt/todo.txt

Actually curating (adding / removing tasks) the todo list is left entirely to
the user. This is intended solely for quickly filtering and displaying tasks.

The script takes a single command line argument which is the path to the todo
list. 
"""

import os
import sys


def invalid_command_error(command: str) -> None:
    """Prints the error message arising from an invalid command word."""
    
    post = " "
    if command[:3] == "fil" or command[:3] == "ful" or command[:3] == "fol":
        post += "Did you mean 'filter'?"
    elif command[:3] == "pro" or command[:3] == "por":
        post += "Did you mean 'projects'?"
    error_msg = "Invalid command '{}'.".format(command) + post
    print(error_msg)
    print("Type 'help' for a list of commands.")
    print("-"*80)


def arg_syntax_error(op: str, tag: str) -> None:
    """Prints the error message arising from a tag syntax error."""
    
    print("Syntax error. Did you mean {}{}?".format(op, tag))
    print("-"*80)


def missing_tag_error(op: str) -> None:
    """Prints the error message arising from a missing tag error."""
    
    print("Syntax error. Missing tag after {}.".format(op))
    print("-"*80)


def priority_error() -> None:
    """Prints the error message arising from multiple priorites error."""
    
    print("Syntax error. Tasks cannot have multiple priorities.")
    print("If you would like to see priority A or priority B tasks")
    print("please use the pipe operator '|' to chain priorities (A)|(B).")
    print("-"*80)


def __get_priority(priority: str, task_list: list) -> list:
    """Gets the tasks in task_list which match the specified priority."""
    
    _tasks = []
    for task in task_list:
        if task[0] != 'x':
            if task[0:3] == priority:
                _tasks.append(task.strip('\n'))
            elif task[0] == 'x':
                if task[2:5] == priority:
                    _tasks.append(task.strip('\n'))
    return _tasks


def get_priority(file: str, priority: str, *args: str, **kwargs: str) -> None:
    """Recursivley filter the tasks matching the priority"""
    
    tasks = kwargs.get("tasks")
    _tasks = get_tasks(file, tasks, __get_priority, priority)
    return process_next(file, *args, tasks = _tasks)


def __get_project(project: str, task_list: list) -> list:
    """Filters task_list, keeping the tasks that match the specified project."""
    
    _tasks = []
    for task in task_list:
        if project in task:
            _tasks.append(task.strip('\n'))
    return _tasks


def get_project(file: str, project: str, *args: str, **kwargs: list) -> None:
    """Recursivley filter the tasks matching the project"""
    
    tasks = kwargs.get("tasks")
    _tasks = get_tasks(file, tasks, __get_project, project)
    return process_next(file, *args, tasks = _tasks)


def __get_context(context: str, task_list: list) -> list:
    """Filters task_list, keeping the tasks that match the specified context."""

    _tasks = []
    for task in task_list:
        if context in task:
            _tasks.append(task.strip('\n'))
    return _tasks


def get_context(file: str, context: str, *args: str, **kwargs: list) -> None:
    """Recursivley filter the tasks matching the context"""
    
    tasks = kwargs.get("tasks")
    _tasks = get_tasks(file, tasks, __get_context, context)
    return process_next(file, *args, tasks = _tasks)


def __get_key(key: str, task_list: list) -> list:
    """Filters task_list, keeping the tasks that match the specified key."""
    
    _tasks = []
    for task in task_list:
        if key in task:
            _tasks.append(task.strip('\n'))
    return _tasks


def get_key(file: str, key: str, *args: str, **kwargs: list) -> None:
    """Recursivley filter the tasks matching the key"""
    
    tasks = kwargs.get("tasks")
    _tasks = get_tasks(file, tasks, __get_key, key)
    return process_next(file, *args, tasks = _tasks)


def get_tasks(file: str, tasks: list, handle, arg: str) -> list:
    """Forwards the filtering of tasks."""
    
    if tasks == None:
        with open(file, "r") as f:
            return handle(arg, f)
    else:
        return handle(arg, tasks)


def process_next(file: str, *args: str, **kwargs: list) -> list:
    """Recursively filters by the next argument and expanding logical OR args."""

    _tasks = kwargs.get("tasks")

    def expand_OR(file: str, args: list, _tasks: list, handle) -> list:
        """Expand logical OR arguments, forwarding to the relevent handle."""

        _ = []
        if '|' in args[0]:
            a = args[0].split('|')
            if _tasks is None:
                _ = handle(file, a[0])
            else:
                _ = handle(file, a[0], tasks = _tasks)

            while len(a) > 0:
                _ += handle(file, a[0], tasks = _tasks)
                a.pop(0)
        else:    
            _ = handle(file, args[0], tasks = _tasks)
        return _
    

    def check_recursion(file: str, args: list, _tasks: list, handle) -> list:
        """Check whether recursion is required or whether this is the end."""

        if (len(args) == 1):
            return _tasks
        else:
            return handle(file, args[1], *args[2::], tasks = _tasks)

    # base case
    if len(args) == 0:
        return _tasks

    # syntax error - no arguments are a single character
    if len(args[0]) == 1:
        arg_syntax_error(args[0], args[1])
        return []

    # handle the arguments - recurse if necessary
    if args[0][0] == '+':
        _ = expand_OR(file, args, _tasks, get_project)
        return check_recursion(file, args, _, get_project)    
    elif args[0][0] == '@':
        _ = expand_OR(file, args, _tasks, get_context)
        return check_recursion(file, args, _, get_context)
    elif args[0][0] == '(':
        _ = expand_OR(file, args, _tasks, get_priority)
        return check_recursion(file, args, _, get_priority)
    elif ':' in args[0]:
        _ = expand_OR(file, args, _tasks, get_key)
        return check_recursion(file, args, _, get_key)


def filter_active(tasks: list) -> list:
    """Filters out only active tasks."""
    
    _tasks = []
    for task in tasks:
        if task[0] != 'x':
            _tasks.append(task)

    return _tasks


def filter_closed(tasks: list) -> list:
    """Filters out only closed tasks."""
    
    _tasks = []
    for task in tasks:
        if task[0] == 'x':
            _tasks.append(task)

    return _tasks


def print_tasks(tasks: list) -> None:
    """Displays the tasks."""
    
    if tasks == []:
        return
    print('')
    for task in tasks:
        print(task)
    print("-"*80)


def get_all_tasks(file: str) -> None:
    """Retrieves all tasks in the todo list."""
    
    _tasks = []
    with open(file, "r") as f:
        for task in f:
            _tasks.append(task.strip('\n'))
    return _tasks


def get_project_tags(file: str) -> list:
    """Retrieves all project tags in use within the todo list."""
    
    project_tags = []
    with open(file, "r") as f:
        for task in f:
            words = task.split(" ")
            for word in words:
                if word[0] == '+':
                    w = word.strip('\n')
                    if w not in project_tags:
                        project_tags.append(w)
    return project_tags


def show_help() -> None:
    """'displays the help message to the user."""
    
    print("")
    print("Commands")
    print('-'*80)
    print("'filter'\tFilter active tasks by project, priority, context and keys.")
    print("\t\tIf no arguments are passed to filter, it will show active tasks.")
    print("\t\t'-all' Shows all tasks for the specified filters.")
    print("\t\t'-closed' Shows only closed tasks for the specified filters.")
    print("'projects'\tLists all the project tags in use.")
    print("'help'\t\tYou're already here.")
    print("'end'\t\tExit program.")
    print("'clear'\t\tClears the screen.\n\n")
    print("Exmaple:")
    print("Let's get the highest priority phone-based tasks relating to")
    print("home repair that are due today.\n")
    print("filter (A) +homeRepair @phone due:2021-22-02\n")


def repl(file: str) -> None:
    """Gather and process user input."""
    
    print("Welcome to the TODO list filter-er")
    print("-"*80)

    while True:
        tasks = []
        user_input  = input(">> ")
        if user_input == "":
            continue
        
        args = user_input.split(' ')
        command = args[0].lower()
        if command == "filter":
            
            show_all = False
            show_closed = False

            if len(args) == 1:
                tasks = get_all_tasks(file)
            elif len(args) == 2:
                if args[1] == "-all":
                    show_all = True
                    args = [args[0]] + args[2::]

                if args[1] == "-closed":
                    show_closed = True
                    args = [args[0]] + args[2::]
                
                if args[1][0] == '+':
                    if (len(args[1]) == 1):
                        missing_tag_error(args[1])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        tasks = get_project(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_project(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_project(file, args[1])
                elif args[1][0] == '(':
                    if (len(args[1]) == 1):
                        missing_tag_error(args[1])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        tasks = get_priority(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_priority(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_priority(file, args[1])
                elif args[1][0] == '@':
                    if (len(args[1]) == 1):
                        missing_tag_error(args[1])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        tasks = get_context(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_context(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_context(file, args[1])
                elif ':' in args[1]:
                    tasks = get_key(file, args[1])
            else:
                priority_count = 0
                for arg in args:
                    if arg[0] == '(':
                        priority_count += 1
                if priority_count > 1:
                    priority_error()
                    continue

                if args[1] == "-all":
                    show_all = True
                    args = [args[0]] + args[2::]

                if args[1] == "-closed":
                    show_closed = True
                    args = [args[0]] + args[2::]
                
                if args[1][0] == '+':
                    if (len(args[1]) == 1):
                        arg_syntax_error(args[1], args[2])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        print(a)
                        tasks = get_project(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_project(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_project(file, args[1], *args[2::])
                elif args[1][0] == '(':
                    if (len(args[1]) == 1):
                        arg_syntax_error(args[1], args[2])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        tasks = get_priority(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_priority(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_priority(file, args[1], *args[2::])
                elif args[1][0] == '@':
                    if (len(args[1]) == 1):
                        arg_syntax_error(args[1], args[2])
                        continue
                    if '|' in args[1]:
                        a = args[1].split('|')
                        tasks = get_context(file, a[0], *args[2::])
                        a.pop(0)
                        while len(a) > 0:
                            tasks += get_context(file, a[0], *args[2::])
                            a.pop(0)
                    else:    
                        tasks = get_context(file, args[1], *args[2::])
                elif ':' in args[1]:
                    tasks = get_key(file, args[1], *args[2::])

            if (show_closed):
                tasks = filter_closed(tasks)
                print_tasks(tasks)
                continue

            if (show_all):
                print_tasks(tasks)
                continue
            
            tasks = filter_active(tasks)    
            print_tasks(tasks)
        elif command == "end":
            break;
        elif command == "projects":
            projects = get_project_tags(file)
            print_tasks(projects)
        elif command == 'clear':
            os.system('cls')
            print("Welcome to the TODO list filter")
            print("-"*80)
        elif command == "help":
            show_help()
        else:
            invalid_command_error(command)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Missing filename.")
    elif len(sys.argv) == 2:
        os.system('cls')
        file = sys.argv[1]
        repl(file)
    else:
        print("Too many command line arguments.")

