import React from "react";

const ShiftSchedule = ({ schedule }) => {
  const getDayOfWeek = (index) => {
    const daysOfWeek = [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ];
    return daysOfWeek[index];
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

  const getColor = (value) => {
    return value === "1" ? "green" : "red";
  };

  return (
    <div>
      <table>
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
                <td
                  key={day}
                  style={{
                    backgroundColor: getColor(schedule[day * 3 + shift]),
                  }}
                ></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ShiftSchedule;
