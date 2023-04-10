@echo off
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\central_index.py"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 1823"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 4082"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 4084"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 1843"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 4062"
timeout /t 2
start powershell.exe -NoExit -Command "cd 'C:\Users\Abheek\Desktop\01_Mondal_Abheek_PA4\CS550_PA2_AMondal'; python .\peer_node.py 4064"