import React, { useEffect, useState, useMemo } from "react";
import { Box, Typography, MenuItem, Select } from "@mui/material";
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";
import { Bar, Pie, Line, Bubble } from "react-chartjs-2";
import { MaterialReactTable } from "material-react-table";
import AxiosInstance from "./Axios";
import "chart.js/auto"; // Automatically register Chart.js components
import ChartDataLabels from "chartjs-plugin-datalabels"; // Import the datalabels plugin
import { getClubNameForAthlete } from "../utils/helpers"; // Import utility function to get club name for athlete

// Register required Chart.js components
ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, ChartDataLabels);

const Dashboard = () => {
  const [clubsData, setClubsData] = useState([]);
  const [athletesData, setAthletesData] = useState([]);
  const [annualVisaData, setAnnualVisaData] = useState([]);
  const [competitionsData, setCompetitionsData] = useState([]);
  const [categoriesData, setCategoriesData] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState("");
  const [teamsData, setTeamsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const clubsResponse = await AxiosInstance.get("/club/");
        const athletesResponse = await AxiosInstance.get("/athlete/");
        const annualVisaResponse = await AxiosInstance.get("/annual-visa/");
        const competitionsResponse = await AxiosInstance.get("/competition/");
        const categoriesResponse = await AxiosInstance.get("/category/");
        const teamsResponse = await AxiosInstance.get("/team/");

        // Aggregate data for clubs
        const clubsWithAggregatedData = clubsResponse.data.map((club) => {
          const clubAthletes = athletesResponse.data.filter((athlete) => athlete.club === club.id);

          // Filter valid and expired visas based on the API structure
          const validVisas = clubAthletes.filter((athlete) =>
            annualVisaResponse.data.some(
              (visa) => visa.athlete === athlete.id && visa.is_valid === true && visa.visa_status === "available"
            )
          );

          const expiredVisas = clubAthletes.filter((athlete) =>
            annualVisaResponse.data.some(
              (visa) => visa.athlete === athlete.id && visa.is_valid === false && visa.visa_status === "expired"
            )
          );

          return {
            ...club,
            athlete_count: clubAthletes.length,
            valid_visa_count: validVisas.length,
            expired_visa_count: expiredVisas.length,
          };
        });

        setClubsData(clubsWithAggregatedData);
        setAthletesData(athletesResponse.data);
        setAnnualVisaData(annualVisaResponse.data);
        setCompetitionsData(competitionsResponse.data);
        setCategoriesData(categoriesResponse.data);
        setTeamsData(teamsResponse.data);

        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const clubsResponse = await AxiosInstance.get("/club/");
        const athletesResponse = await AxiosInstance.get("/athlete/");

        console.log("Clubs Data:", clubsResponse.data);
        console.log("Athletes Data:", athletesResponse.data);

        setClubsData(clubsResponse.data);
        setAthletesData(athletesResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  // Ensure hooks are always called, even if data is not yet available
  const filteredData = useMemo(() => {
    if (!selectedCompetition || !competitionsData.length || !categoriesData.length) return [];
    const competition = competitionsData.find((comp) => comp.id === parseInt(selectedCompetition));
    if (!competition) return [];

    const assignedCategories = categoriesData.filter((category) => category.competition === competition.id);

    return assignedCategories.map((category) => {
      if (category.type === "solo") {
        return {
          categoryName: category.name,
          awards: {
            firstPlace: category.first_place_name || "N/A",
            firstPlaceClub: getClubNameForAthlete(category.first_place_athlete_id, athletesData, clubsData),
            secondPlace: category.second_place_name || "N/A",
            secondPlaceClub: getClubNameForAthlete(category.second_place_athlete_id, athletesData, clubsData),
            thirdPlace: category.third_place_name || "N/A",
            thirdPlaceClub: getClubNameForAthlete(category.third_place_athlete_id, athletesData, clubsData),
          },
          athletes: category.enrolled_athletes?.map((enrollment) => {
            const athlete = athletesData.find((a) => a.id === enrollment.athlete);
            const clubName = getClubNameForAthlete(athlete?.id, athletesData, clubsData);
            return athlete ? `${athlete.first_name} ${athlete.last_name} (${clubName})` : "Unknown";
          }) || [],
        };
      } else if (category.type === "teams") {
        return {
          categoryName: category.name,
          awards: {
            firstPlace: category.first_place_team_name || "N/A",
            firstPlaceClub: (() => {
              const firstTeam = teamsData.find((team) => team.id === category.first_place_team_id);
              const firstAthleteId = firstTeam?.members?.[0]?.athlete?.id;
              return getClubNameForAthlete(firstAthleteId, athletesData, clubsData);
            })(),
            secondPlace: category.second_place_team_name || "N/A",
            secondPlaceClub: (() => {
              const secondTeam = teamsData.find((team) => team.id === category.second_place_team_id);
              const firstAthleteId = secondTeam?.members?.[0]?.athlete?.id;
              return getClubNameForAthlete(firstAthleteId, athletesData, clubsData);
            })(),
            thirdPlace: category.third_place_team_name || "N/A",
            thirdPlaceClub: (() => {
              const thirdTeam = teamsData.find((team) => team.id === category.third_place_team_id);
              const firstAthleteId = thirdTeam?.members?.[0]?.athlete?.id;
              return getClubNameForAthlete(firstAthleteId, athletesData, clubsData);
            })(),
          },
          teams: category.teams?.map((teamId) => {
            const team = teamsData.find((team) => team.id === teamId);
            const firstAthleteId = team?.members?.[0]?.athlete?.id;
            const firstAthleteClub = getClubNameForAthlete(firstAthleteId, athletesData, clubsData);
            return `${team?.name || "Unknown Team"} (${firstAthleteClub})`;
          }) || [],
        };
      }
      return null; // Fallback for unknown category types
    }).filter((category) => category !== null); // Remove null entries
  }, [selectedCompetition, competitionsData, categoriesData, athletesData, clubsData, teamsData]);

  const totalCategories = useMemo(() => filteredData.length, [filteredData]);
  const totalUniqueAthletes = useMemo(() => {
    const uniqueAthletes = new Set();
    filteredData.forEach((category) => {
      if (category.athletes) {
        category.athletes.forEach((athlete) => uniqueAthletes.add(athlete));
      }
      if (category.teams) {
        category.teams.forEach((team) => uniqueAthletes.add(team));
      }
    });
    return uniqueAthletes.size;
  }, [filteredData]);

  const columns = useMemo(
    () => [
      {
        accessorKey: "categoryName",
        header: "Category",
      },
      {
        accessorKey: "awards",
        header: "Awards",
        Cell: ({ cell }) => {
          const awards = cell.getValue();
          return (
            <Box>
              <Typography>
                🥇 {awards.firstPlace ? `${awards.firstPlace} (${awards.firstPlaceClub || "Unknown Club"})` : "N/A"}
              </Typography>
              <Typography>
                🥈 {awards.secondPlace ? `${awards.secondPlace} (${awards.secondPlaceClub || "Unknown Club"})` : "N/A"}
              </Typography>
              <Typography>
                🥉 {awards.thirdPlace ? `${awards.thirdPlace} (${awards.thirdPlaceClub || "Unknown Club"})` : "N/A"}
              </Typography>
            </Box>
          );
        },
      },
      {
        accessorKey: "enrolled",
        header: "Enrolled Athletes/Teams",
        Cell: ({ row }) => {
          const category = row.original;
          if (category.athletes) {
            return <Typography>{category.athletes.length} Athletes</Typography>;
          } else if (category.teams) {
            return <Typography>{category.teams.length} Teams</Typography>;
          }
          return <Typography>0</Typography>;
        },
      },
    ],
    []
  );

  // Calculate totals for all clubs
  const totalAthletes = clubsData.reduce((sum, club) => sum + club.athlete_count, 0);
  const totalValidVisas = clubsData.reduce((sum, club) => sum + club.valid_visa_count, 0);
  const totalExpiredVisas = clubsData.reduce((sum, club) => sum + club.expired_visa_count, 0);

  const horizontalBarChartData = {
    labels: clubsData.map((club) => club.name),
    datasets: [
      {
        label: `Total Athletes (${totalAthletes})`,
        data: clubsData.map((club) => club.athlete_count),
        backgroundColor: "rgba(75, 192, 192, 0.8)",
      },
      {
        label: `Valid Annual Visa (${totalValidVisas})`,
        data: clubsData.map((club) => club.valid_visa_count),
        backgroundColor: "rgba(54, 162, 235, 0.8)",
      },
      {
        label: `Expired Annual Visa (${totalExpiredVisas})`,
        data: clubsData.map((club) => club.expired_visa_count),
        backgroundColor: "rgba(255, 99, 132, 0.8)",
      },
    ],
  };

  const horizontalBarChartOptions = {
    indexAxis: "y", // Horizontal bar chart
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const clubIndex = context.dataIndex;
            const club = clubsData[clubIndex];
            const datasetLabel = context.dataset.label;
            if (datasetLabel === "Total Athletes") {
              return `Total Athletes: ${club.athlete_count}`;
            } else if (datasetLabel === "Valid Annual Visa") {
              return `Valid Annual Visa: ${club.valid_visa_count}`;
            } else if (datasetLabel === "Expired Annual Visa") {
              return `Expired Annual Visa: ${club.expired_visa_count}`;
            }
          },
        },
      },
      datalabels: {
        anchor: "middle",
        align: "center",
        color: "#000",
        font: {
          weight: "bold",
        },
        formatter: (value) => {
          // Only show labels if the value is not 0
          return value !== 0 ? value : null;
        },
      },
    },
    responsive: true,
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          stepSize: 1, // Ensure scale numbers are integers
          callback: (value) => (Number.isInteger(value) ? value : null),
        },
      },
      y: {
        ticks: {
          font: {
            weight: "bold", // Make club names bolder
          },
        },
        grid: {
          drawBorder: false,
          color: "rgba(0, 0, 0, 0.2)", // Light grid lines
          borderWidth: 2, // Bolder divider between clubs
          lineWidth: 2, // Thickness of the divider
        },
      },
    },
    elements: {
      bar: {
        barThickness: 20, // Increase bar thickness
        categoryPercentage: 0.8, // Add better separation between bars
      },
    },
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!clubsData.length || !athletesData.length) {
    return <div>No data available to display.</div>;
  }

  return (
    <Box>

      {/* Horizontal Bar Chart */}
      <Box sx={{ marginBottom: 4 }}>
        <Typography variant="h6">Clubs Overview</Typography>
        <Bar data={horizontalBarChartData} options={horizontalBarChartOptions} />
      </Box>

      <Box sx={{ marginBottom: 2 }}>
        <Typography variant="h6">Competitions</Typography>
        <Select
          sx={{ marginTop: 2 }}
          value={selectedCompetition}
          onChange={(e) => setSelectedCompetition(e.target.value)}
          fullWidth
          displayEmpty
        >
          <MenuItem value="" disabled>
            Select a competition
          </MenuItem>
          {competitionsData.map((competition) => (
            <MenuItem key={competition.id} value={competition.id}>
              {competition.name}
            </MenuItem>
          ))}
        </Select>
      </Box>

      <Box>
        <MaterialReactTable
          columns={columns}
          data={filteredData}
          enableRowActions={false}
          renderBottomToolbarCustomActions={() => (
            <Box sx={{ padding: 2 }}>
              <Typography variant="body1">Total Categories: {totalCategories}</Typography>
              <Typography variant="body1">Total Athletes Enrolled: {totalUniqueAthletes}</Typography>
            </Box>
          )}
        />
      </Box>
    </Box>
  );
};

export default Dashboard;