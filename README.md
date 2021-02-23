# TODO_filterer
This is a short CLI program to filter and display a TODO list.

This allows filtering by task priority, project tag, context tag and user defined keys. Filters of the same kind can be OR'd together to show, for example, all tasks with priority A or B. The todo list must be formatted according to https://github.com/todotxt/todo.txt. When run, the script requires one command line argument (the path to the todo list). The program will drop you into a repl where you can filter your todo list. There are currently two flags that can be set (only one at a time): '-all' and '-closed'. '-all' shows both closed and open tasks, whereas '-closed' shows only closed tasks. If not flags are provided, only active tasks are displayed. 

Currently implemented commands are:
'filter'
'projects'
'help'
'clear'
'end'

Example usage:
`filter (C)|(D) +garage @phone` This command will show all priority C and priority D tasks relating to the +garage project and the @phone context.

`filter -closed (A) +garage` This command would show all of the closed priority A tasks relating to the +garage project.

`filter -all (D) +gameNight @phone friend:Dan` This command would show all (open and closed) priority D tasks relating to the gameNight project, with the ~phone context and with the friend:Dan user defined key:value.
