import React from "react";
import "../styles/Shift.css";

const ShiftSchedule = ({ schedule }) => {
  if (!schedule || typeof schedule !== "string" || schedule.length !== 21) {
    return <div>Error: Invalid schedule string.</div>;
  }

  const getDayOfWeek = (index) => {
    const daysOfWeek = [
      "Monday", "Thuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ];
    return daysOfWeek[index];
  };

  const getScheduleHours = (index) => {
    const hours = ["6-14", "14-22", "22-6"];
    return hours[index];
  };

  const getShiftLabel = (index) => {
    switch (index) {
      case 0:
        return "Morning";
      case 1:
        return "Afternoon";
      case 2:
        return "Night";
      default:
        return "";
    }
  };

  return (
    <div className="table-container">
      <table className="schedule-table">
        <thead>
          <tr>
            <th></th>
            {[0, 1, 2, 3, 4, 5, 6].map((day) => (
              <th key={day}>{getDayOfWeek(day)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[0, 1, 2].map((shift) => (
            <tr key={shift}>
              <td>{getShiftLabel(shift)}</td>
              {[0, 1, 2, 3, 4, 5, 6].map((day) => (
                <td key={day} className="schedule-cell">
                  <p
                    style={{
                      color:
                        schedule.charAt(day * 3 + shift) === "1"
                          ? "green"
                          : "red",
                    }}
                  >
                    {schedule.charAt(day * 3 + shift) == 1
                      ? getScheduleHours((day * 3 + shift) % 3)
                      : "Off"}
                  </p>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ShiftSchedule;
