| #   | What it does | Method | Path | Request body | Success code | Error codes |
|-----|--------------|--------|------|--------------|--------------|-------------|
| E1  | Get all the machines. Can be filtered by block and kind. Each one includes its state, and minutes left if running. | get	| 	/machines|none | | |
| E2  | Get one machine by its id, with its last 5 runs. |get | /machines/{id}| none| | |
| E3  | Add a machine: name, block, kind and cycle minutes. It starts in service. | post|/machines | | | |
| E4  | Mark a machine out of order or back in service. | pach|/machines/{id}/state | | | |
| E5  | Start a machine with a roll number. It starts now and ends after the machine's cycle minutes. | post|/machines/{id}/+ | | | |
| E6  | Collect clothes from a run, with the roll number of the student who started it. |pach | | | | |
| E7  | Clear a machine whose clothes weren't collected, with your roll number. The run becomes `cleared`. |pach | | | | |
| E8  | Get one student's runs that aren't collected or cleared, by roll number. Each one includes the machine's name and minutes left. |get | | | | |
| E9  | Get the machines that need attention: out of order, or waiting for pickup for more than 15 minutes. | get| | | | |
| E10 | Get today's usage: for each block, the number of washer runs and dryer runs started. |get | | | | |
