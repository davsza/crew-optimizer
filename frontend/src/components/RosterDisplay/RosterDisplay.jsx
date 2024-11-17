import { getRosterDisplayParameters } from "../../constants";
import "./RosterDisplay.css";
import { getBuiltInStrings } from "../../constants";
import RosterComponent from "../RosterComponent/RosterComponent";

const RosterDisplay = ({
  scheduleOfTheDay,
  appliedScheduleOfTheDay,
  highlighted,
  workDays,
  offDays,
  reserveDays,
  vacation,
  sickness,
  reserveCallIn,
  dayOffCallIn,
  published,
  day,
  application,
}) => {
  return (
    <div
      className={`outer ${highlighted ? "highlighted" : ""} ${
        reserveCallIn[day] === "1" ? "reserveCallIn" : ""
      } ${dayOffCallIn[day] === "1" ? "dayOffCallIn" : ""}`}
    >
      {(workDays[day] === "1" || reserveCallIn[day] === "1" || application) &&
      vacation[day] !== "1" &&
      sickness[day] !== "1" ? (
        scheduleOfTheDay.map((roster, index) => {
          const { from, to, applicationForSchedule, style } =
            getRosterDisplayParameters(roster, index, appliedScheduleOfTheDay);
          return (
            <div
              key={index}
              className={`inner ${
                applicationForSchedule === "1" && !application
                  ? "application"
                  : ""
              }`}
              style={style}
            >
              {from} - {to}
            </div>
          );
        })
      ) : sickness[day] === "1" ? (
        <RosterComponent
          content={getBuiltInStrings.SICKNESS}
          backgroundColor="orange"
        />
      ) : vacation[day] === "1" ? (
        <RosterComponent
          content={getBuiltInStrings.VACATION_CLAIM}
          backgroundColor="purple"
        />
      ) : offDays[day] === "1" ? (
        <RosterComponent
          content={getBuiltInStrings.DAY_OFF}
          backgroundColor="green"
        />
      ) : reserveDays[day] === "1" ? (
        <RosterComponent
          content={getBuiltInStrings.RESERVE}
          backgroundColor="blue"
        />
      ) : (
        <div>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</div>
      )}
    </div>
  );
};

export default RosterDisplay;
