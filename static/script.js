document.addEventListener('DOMContentLoaded', () => {
    const projectFilterInputs = document.querySelectorAll('[id^="project-filter-"]');
    const tableRows = document.querySelectorAll('tbody tr');

    projectFilterInputs.forEach(projectFilterInput => {
        projectFilterInput.addEventListener('input', () => {
            const filterValue = projectFilterInput.value.trim().toLowerCase();

            tableRows.forEach((row) => {
                const project = row.dataset.project.toLowerCase();

                if (project.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });


    // function updateDueDate(taskId) {
    //     const dueDateInput = document.getElementById(`due-date-${taskId}`);
    //     const dueDate = dueDateInput.value;
    //     const durationInput = document.getElementById(`duration-${taskId}`);
    //     const duration = durationInput.value;

    //     const data = {
    //         task_id: taskId,
    //         due_datetime: dueDate,
    //         duration: duration
    //     };

    //     fetch('/update-due-date', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify(data)
    //     })
    //     .then(response => response.json())
    //     .then(result => {
    //         if (result.status === 'success') {
    //             const updatedTask = result.task;
    //             const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
    //             dueDateCell.value = updatedTask.due.datetime;
    //         } else {
    //             alert('Failed to update due date');
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Error:', error);
    //     });
    // }

});


// Function to set the due date of a task to today's noon
function setDueDateToToday(taskId) {
    const dueDateInput = document.getElementById(`due-date-${taskId}`);
    const today = new Date();
    today.setHours(12, 0, 0); // Set the time to noon

    const formattedDate = today.toISOString().slice(0, 16); // Format the date as 'YYYY-MM-DDTHH:mm'

    dueDateInput.value = formattedDate;
}


function updateToday(event, button, taskId) {
    button.disabled = true;
    const now = new Date();
    now.setHours(12, 0, 0, 0); // Set the time to today's noon (12:00 PM)

    const dueDateInput = document.getElementById(`due-date-${taskId}`);
    const durationInput = document.getElementById(`duration-${taskId}`);
    const duration = durationInput.value;

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const dueDate = `${year}-${month}-${day}T${hours}:${minutes}`;

    const data = {
        task_id: taskId,
        due_datetime: dueDate
    };


    fetch('/update-due-date', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                const updatedTask = result.task;
                const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
                dueDateCell.value = updatedTask.due.datetime;
            } else {
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function updateTomorrow(event, button, taskId) {
    button.disabled = true;
    const now = new Date();
    now.setDate(now.getDate() + 1); // Set the date to tomorrow

    now.setHours(12, 0, 0, 0); // Set the time to today's noon (12:00 PM)

    const dueDateInput = document.getElementById(`due-date-${taskId}`);
    const durationInput = document.getElementById(`duration-${taskId}`);
    const duration = durationInput.value;

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const dueDate = `${year}-${month}-${day}T${hours}:${minutes}`;

    const data = {
        task_id: taskId,
        due_datetime: dueDate
    };


    fetch('/update-due-date', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                const updatedTask = result.task;
                const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
                dueDateCell.value = updatedTask.due.datetime;
            } else {
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function plusOneDay(event, button, taskId) {
    button.disabled = true;
    const now = new Date();
    now.setDate(now.getDate() + 1); // Set the date to tomorrow

    now.setHours(12, 0, 0, 0); // Set the time to today's noon (12:00 PM)
    
    // Get the duration input for the task
    const durationInput = document.getElementById(`duration-${taskId}`);
    const duration = durationInput.value;

    // Get the current due date input value
    const dueDateInput = document.getElementById(`due-date-${taskId}`);
    const currentDueDate = new Date(dueDateInput.value);

    // Add one day to the current due date
    currentDueDate.setDate(currentDueDate.getDate() + 1);

    // Set the time to tomorrow's noon (12:00 PM)
    currentDueDate.setHours(12, 0, 0, 0);

    // Format the due date as a string in the format "YYYY-MM-DDTHH:MM"
    const year = currentDueDate.getFullYear();
    const month = String(currentDueDate.getMonth() + 1).padStart(2, '0');
    const day = String(currentDueDate.getDate()).padStart(2, '0');
    const hours = String(currentDueDate.getHours()).padStart(2, '0');
    const minutes = String(currentDueDate.getMinutes()).padStart(2, '0');
    const dueDate = `${year}-${month}-${day}T${hours}:${minutes}`;

    // Prepare the data to be sent to the server
    const data = {
        task_id: taskId,
        due_datetime: dueDate
    };

    fetch('/update-due-date', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                const updatedTask = result.task;
                const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
                dueDateCell.value = updatedTask.due.datetime;
            } else {
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// function updateDueDate(taskId) {
//     const now = new Date();
//     now.setHours(12, 0, 0, 0); // Set the time to today's noon (12:00 PM)

//     const dueDateInput = document.getElementById(`due-date-${taskId}`);
//     const durationInput = document.getElementById(`duration-${taskId}`);
//     const followUpCheckbox = document.getElementById(`follow-up-${taskId}`);
//     const labelsTextarea = document.getElementById(`labels-${taskId}`);

//     const dueDate = now.toISOString(); // Convert the date to ISO 8601 format
//     const duration = durationInput.value;
//     const followUp = followUpCheckbox.checked;
//     const labels = labelsTextarea.value.split('\n').filter(label => label.trim() !== '');

//     if (followUp) {
//         labels.push('Followup'); // Add 'Followup' label if the Follow Up checkbox is checked
//     }

//     const data = {
//         task_id: taskId,
//         due_datetime: dueDate,
//         duration: duration,
//         labels: labels
//     };

//     fetch('/update-due-date', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     })
//     .then(response => response.json())
//     .then(result => {
//         if (result.status === 'success') {
//             const updatedTask = result.task;
//             const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
//             dueDateCell.value = updatedTask.due.datetime;
//         } else {
//             alert('Failed to update due date');
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }

function updateDueDate(event, button, taskId) {
    button.disabled = true;
    const taskContentInput = document.getElementById(`task-content-${taskId}`);
    const taskContent = taskContentInput.value;
    const dueDateInput = document.getElementById(`due-date-${taskId}`);
    const dueDate = dueDateInput.value;
    const durationInput = document.getElementById(`duration-${taskId}`);
    const duration = durationInput.value;
    const followUpCheckbox = document.getElementById(`follow-up-${taskId}`);
    const labelsTextarea = document.getElementById(`labels-${taskId}`);
    const followUp = followUpCheckbox.checked;
    const labels = labelsTextarea.value.split('\n').filter(label => label.trim() !== '');

    if (followUp) {
        labels.push('Followup'); // Add 'Followup' label if the Follow Up checkbox is checked
    }


    const data = {
        task_id: taskId,
        due_datetime: dueDate,
        duration: duration,
        labels: labels,
        content: taskContent
    };

    fetch('/update-due-date', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                const updatedTask = result.task;
                const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
                dueDateCell.value = updatedTask.due.datetime;
            } else {
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// function saveNotepad(button, name) {
//     button.disabled = true;
//     const notepadContent = document.getElementById('notepad').value;
//     const element = document.createElement('a');
//     element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(notepadContent));
//     element.setAttribute('download', name+'.txt');
//     element.style.display = 'none';
//     document.body.appendChild(element);
//     element.click();
//     document.body.removeChild(element);
//     button.disabled = false;
// }

function createTask(event, button, date) {
    button.disabled = true;
    const taskText = document.getElementById('addTask').value;


    const now = new Date();
    now.setHours(12, 0, 0, 0); // Set the time to today's noon (12:00 PM)

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const dueDate = `${year}-${month}-${day}T${hours}:${minutes}`;

    const labelsTextarea = document.getElementById(`addTask-labels`);
    const labels = labelsTextarea.value.split('\n').filter(label => label.trim() !== '');
    const followUpCheckbox = document.getElementById(`addTask-followup`);
    const followUp = followUpCheckbox.checked;

    if (followUp) {
        labels.push('Followup'); // Add 'Followup' label if the Follow Up checkbox is checked
    }
    let data = {
        content: taskText,
        labels: labels
    };

    if (date == 'today') {
        data = {
            content: taskText,
            due_datetime: dueDate
        }
    }

    fetch('/createTask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                // const updatedTask = result.task;
                // const dueDateCell = document.querySelector(`#due-date-${updatedTask.id}`);
                // dueDateCell.value = updatedTask.due.datetime;
                // alert('Success');
            } else {
                button.disabled = false;
                button.style.backgroundColor = 'red';
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            button.disabled = false;
            button.style.backgroundColor = 'red';
            console.error('Error:', error);
        });
}


function closeTask(event, button, taskId) {
    button.disabled = true;
    console.log('taskId: ' + taskId)
    const data = {
        task_id: taskId
    };

    fetch('/closeTask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
            } else {
                alert('Failed to update due date');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function saveNotepad(button, noteId) {
    button.disabled = true;
    const notepadContent = document.getElementById('notepad' + noteId).value;

    fetch('/saveNotepad', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: notepadContent, noteId: noteId })
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                button.disabled = false;
                // Success, do something if needed
            } else {
                button.disabled = false;
                button.style.backgroundColor = 'red';
                alert('Failed to save notepad content');
            }
        })
        .catch(error => {
            button.disabled = false;
            button.style.backgroundColor = 'red';
            console.error('Error:', error);
        });
}
const numberOfNotepads = 7;

for (let i = 1; i <= numberOfNotepads; i++) {
    const notepadId = `notepad${i}`;
    window.addEventListener('load', function () {
        fetch(`/getNotepad/${i}`)
            .then(response => response.text())
            .then(content => {
                document.getElementById(notepadId).value = content;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
}


function editTaskContent(cell) {
    var contentDiv = cell.querySelector(".task-content");
    var contentInput = cell.querySelector(".task-content-input");
    contentDiv.style.display = "none";
    contentInput.style.display = "block";
    contentInput.focus();
    contentInput.select();
    contentInput.addEventListener("blur", function () {
        contentDiv.innerHTML = contentInput.value;
        contentInput.style.display = "none";
        contentDiv.style.display = "block";
    });
}

function autoExpand(textarea) {
    // Reset the height to its default value
    textarea.style.height = "auto";

    // Set the height to match the content
    textarea.style.height = textarea.scrollHeight + "px";
}

function saveTimeBlocks() {
    // Get all the input elements for time blocks
    const timeInputs = document.querySelectorAll('.time-block-table input[type="text"]');

    // Create an object to store the time block data
    const timeBlockData = {};

    // Loop through the input elements and save their values to the object
    timeInputs.forEach(input => {
        const timeId = input.id;
        const task = input.value;
        timeBlockData[timeId] = task;
    });

    // Now you have the time block data in the timeBlockData object
    // You can proceed to save it to the server using fetch or perform other operations as needed.
    console.log(timeBlockData);
}

function editTimeBlock(timeBlock) {
    const currentText = timeBlock.textContent;
    const currentColor = timeBlock.style.backgroundColor;

    // Create an input element and set its value to the current text
    const inputElement = document.createElement('input');
    inputElement.type = 'text';
    inputElement.value = currentText;
    timeBlock.textContent = '';
    timeBlock.appendChild(inputElement);

    // Create a color picker element and set its value to the current color
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.value = currentColor;
    timeBlock.appendChild(colorPicker);

    // Create a save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    timeBlock.appendChild(saveButton);

    // Handle the save button click event
    saveButton.addEventListener('click', () => {
        const newText = inputElement.value;
        const newColor = colorPicker.value;
        timeBlock.textContent = newText;
        timeBlock.style.backgroundColor = newColor;
        // Call a function to save the data to the backend
        saveDataToBackend(newText, newColor);
    });
}

function saveDataToBackend(text, color) {
    // Implement the code to save the data to the backend using fetch or any other method.
    // For example, you can use fetch to send the data to your backend API endpoint.
    // Replace 'your-backend-api-endpoint' with the actual URL of your backend API.
    fetch('your-backend-api-endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            color: color,
        }),
    })
        .then(response => {
            // Handle the response from the backend if needed
            console.log('Data saved successfully.');
        })
        .catch(error => {
            console.error('Error saving data:', error);
        });
}


// Function to dynamically generate the time block grid
function generateTimeBlockGrid() {
    updateTimeLeftUntil7PM();
    const timeBlockGrid = document.querySelector(".time-block-grid");

    // Get the current time
    const currentTime = new Date();
    const currentHour = currentTime.getHours();
    const currentMinutes = currentTime.getMinutes();

    // Generate half-hour intervals from 7:00 AM to 11:30 PM
    const startTime = 7;
    const endTime = 23;
    for (let hour = startTime; hour <= endTime; hour++) {
        for (let minutes = 0; minutes < 60; minutes += 30) {
            const time = `${hour.toString().padStart(2, "0")}:${minutes === 0 ? "00" : "30"} ${hour < 12 ? "AM" : "PM"}`;
            const timeElement = document.createElement("div");
            timeElement.classList.add("time");
            timeElement.dataset.time = time;
            timeElement.textContent = time;

            // Check if the current time is within the time block and add a yellow background if true
            if (hour === currentHour && (minutes === 0 || (minutes === 30 && currentMinutes >= 30))) {
                timeElement.style.backgroundColor = "yellow";
            }

            // Check if the time block is 9 AM or 7 PM and add a blue background if true
            if ((hour === 9 && minutes === 0) || (hour === 19 && minutes === 0)) {
                timeElement.style.backgroundColor = "blue";
            }

            // Attach event listener for double-click on time blocks
            timeElement.addEventListener("dblclick", function () {
                editTimeBlock(this);
            });

            timeBlockGrid.appendChild(timeElement);
        }
    }

    // setInterval(updateTimeLeftUntil7PM, 60000);

}


// Function to update the "time left until 7 PM" stamp
function updateTimeLeftUntil7PM() {
    const currentTime = new Date();
    const currentHour = currentTime.getHours();
    const currentMinutes = currentTime.getMinutes();

    // Calculate the time left until 7 PM
    let timeLeft = 0;
    if (currentHour < 19) {
        timeLeft = (19 - currentHour) * 60 - currentMinutes;
    }

    const timeLeftStamp = document.querySelector(".time-left-until-7pm");
    if (timeLeftStamp) {
        // Update the UI with the time left until 7 PM
        if (timeLeft <= 0) {
            timeLeftStamp.textContent = "It's 7 PM now!";
        } else {
            const hoursLeft = Math.floor(timeLeft / 60);
            const minutesLeft = timeLeft % 60;
            timeLeftStamp.textContent = `${hoursLeft}h${minutesLeft}m`;
        }
    }
}

window.addEventListener("load", generateTimeBlockGrid);

// Attach event listener for double-click on time blocks
document.addEventListener("dblclick", function (event) {
    const clickedElement = event.target;
    if (clickedElement.classList.contains("time")) {
        editTimeBlock(clickedElement);
    }
});
