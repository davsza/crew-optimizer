export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh";
export const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
export const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

export const getCurrentWeek = (additionalWeeks) => {
  const now = new Date();
  const yearStart = new Date(now.getFullYear(), 0, 1);
  const oneDay = 1000 * 60 * 60 * 24;
  const startDay = yearStart.getDay();
  const daysToAdd = startDay > 1 ? 8 - startDay : 1 - startDay;
  yearStart.setDate(yearStart.getDate() + daysToAdd);

  const diffFromStart = now - yearStart;
  let weekNumber = Math.floor(diffFromStart / (7 * oneDay)) + 1;

  weekNumber += additionalWeeks;
  return weekNumber;
};

export const getStartDateOfWeek = (year, weekNumber) => {
  const januaryFirst = new Date(year, 0, 1);
  const firstDayOfYear = januaryFirst.getDay() || 7;
  const daysToAdd = (weekNumber - 1) * 7 - (firstDayOfYear - 1);
  const startDate = new Date(year, 0, 1 + daysToAdd);
  startDate.setDate(startDate.getDate() - startDate.getDay() + 1);
  return startDate;
};

export const getEndDateOfWeek = (year, weekNumber) => {
  const januaryFirst = new Date(year, 0, 1);
  const firstDayOfYear = januaryFirst.getDay() || 7;
  const daysToAdd = (weekNumber - 1) * 7 - (firstDayOfYear - 1);
  const startDate = new Date(year, 0, 1 + daysToAdd);
  startDate.setDate(startDate.getDate() - startDate.getDay() + 7);
  return startDate;
};

export const getCurrentYear = () => {
  const now = new Date();
  const currentYear = now.getFullYear();
  return currentYear;
};

export const formatDate = (date) => {
  const options = { month: "short", day: "numeric" };
  return date.toLocaleDateString("en-US", options);
};

export const datePlusDays = (date, days) => {
  const newDate = new Date(date);
  newDate.setDate(newDate.getDate() + days);
  return newDate;
};

export const getStartingHours = (index) => {
  const hours = [6, 10, 14];
  return hours[index];
};

export const getFinishingHours = (index) => {
  const hours = [14, 18, 22];
  return hours[index];
};

export const getDefaultDays = () => {
  return "0000000";
};

export const getRosterDisplayParameters = (
  roster,
  index,
  applicationOfTheDay
) => {
  const from = getStartingHours(index);
  const to = getFinishingHours(index);
  const applicationForSchedule = applicationOfTheDay[index];
  const style = {
    color: roster === "1" ? "#ffffff" : "#007bff",
    backgroundColor: roster === "1" ? "#007bff" : "transparent",
    border: roster !== "1" ? "1px solid #007bff" : "none",
    left: `${(from / 24) * 100}%`,
    width: `${((to - from) / 24) * 100}%`,
  };

  return {
    from,
    to,
    applicationForSchedule,
    style,
  };
};

export const getAdminTableHeader = () => {
  return [
    "Username",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];
};

export const getBuiltInStrings = {
  SELECT_WEEK_STRING: "Select a week",
  SCHEDULE: "Schedule",
  APPLICATION: "Application",
  DAY_OFF: "Day off",
  RESERVE: "Reserve",
  NO_SCHEDULE_TO_DISPLAY: "No schedule to display",
  VACATION: "Vacation",
  VACATION_CLAIM: "Vacation claim",
};

export const formatTimestampToFormattedTime = (timestamp) => {
  const date = new Date(timestamp);

  let hours = date.getHours();
  let minutes = date.getMinutes();

  hours = hours < 10 ? "0" + hours : hours;
  minutes = minutes < 10 ? "0" + minutes : minutes;

  return `${hours}:${minutes}`;
};
