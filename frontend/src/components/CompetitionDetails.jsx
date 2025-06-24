import React, { useEffect, useState } from "react";
import { Typography, Box, IconButton } from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { Link, useParams } from "react-router-dom";
import { MaterialReactTable } from "material-react-table";
import AxiosInstance from "./Axios";

const CompetitionDetails = () => {
  const { competitionId } = useParams(); // Get competition ID from URL
  const [competitionName, setCompetitionName] = useState(""); // Store competition name
  const [categoriesData, setCategoriesData] = useState([]);
  const [teamsData, setTeamsData] = useState([]);
  const [clubsData, setClubsData] = useState([]);
  const [resolvedData, setResolvedData] = useState({});
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const competitionsResponse = await AxiosInstance.get("/competition/");
        const categoriesResponse = await AxiosInstance.get("/category/");
        const teamsResponse = await AxiosInstance.get("/team/");
        const clubsResponse = await AxiosInstance.get("/club/");

        const competition = competitionsResponse.data.find(
          (comp) => comp.id === parseInt(competitionId)
        );
        setCompetitionName(competition?.name || "Competition Details"); // Set competition name

        const filteredCategories = categoriesResponse.data.filter(
          (category) => category.competition === parseInt(competitionId)
        );

        console.log("Filtered Categories for Competition ID:", competitionId, filteredCategories); // Debugging

        setCategoriesData(filteredCategories);
        setTeamsData(teamsResponse.data);
        setClubsData(clubsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setErrorMessage("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [competitionId]);

  useEffect(() => {
    const resolveData = async () => {
      const dataMap = {};
      for (const category of categoriesData) {
        const data = await Promise.all(
          category.type === "teams"
            ? category.teams.map(async (teamId) => {
                const team = teamsData.find((team) => team.id === teamId);
                const teamMembers =
                  team?.members?.map((member) => {
                    const athlete = member.athlete;
                    const club = clubsData.find((club) => club.id === athlete.club);
                    return (
                      <a
                        key={athlete.id}
                        href={`/athletes/${athlete.id}`}
                        style={{ textDecoration: "none", color: "#1976d2" }}
                      >
                        {`${athlete.first_name} ${athlete.last_name} (${club?.name || "Unknown Club"})`}
                      </a>
                    );
                  }) || [];

                // Handle empty teamMembers array
                const combinedTeamMembers =
                  teamMembers.length > 0
                    ? teamMembers.reduce((prev, curr) => [prev, " + ", curr], [])
                    : ["No members"];

                return {
                  athleteOrTeamName: combinedTeamMembers,
                  placement: category.first_place_team === teamId ? "🥇 1st Place" : "Participant",
                };
              })
            : category.enrolled_athletes.map(async (enrollment) => {
                const athlete = enrollment.athlete;
                const club = clubsData.find((club) => club.id === athlete.club);
                return {
                  athleteOrTeamName: (
                    <a
                      href={`/athletes/${athlete.id}`}
                      style={{ textDecoration: "none", color: "#1976d2" }}
                    >
                      {`${athlete.first_name} ${athlete.last_name} (${club?.name || "Unknown Club"})`}
                    </a>
                  ),
                  placement:
                    category.first_place === athlete.id
                      ? "🥇 1st Place"
                      : category.second_place === athlete.id
                      ? "🥈 2nd Place"
                      : category.third_place === athlete.id
                      ? "🥉 3rd Place"
                      : "Participant",
                };
              })
        );
        dataMap[category.id] = data;
      }
      setResolvedData(dataMap);
      console.log("Resolved Data:", dataMap); // Debugging resolved data
    };

    resolveData();
  }, [categoriesData, teamsData, clubsData]);

  if (loading) {
    return <Typography>Loading competition details...</Typography>;
  }

  if (errorMessage) {
    return <Typography color="error">{errorMessage}</Typography>;
  }

  if (categoriesData.length === 0) {
    return (
      <Typography variant="h6" sx={{ padding: 2 }}>
        No categories found for this competition.
      </Typography>
    );
  }

  return (
    <Box>
      {/* Back Arrow */}
      <Box sx={{ display: "flex", alignItems: "center", marginBottom: 2 }}>
        <IconButton component={Link} to="/competitions" sx={{ marginRight: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4">{competitionName}</Typography>
      </Box>

      {categoriesData.map((category) => {
        const columns = [
          { accessorKey: "athleteOrTeamName", header: "Athlete/Team Name (Club)" },
          { accessorKey: "placement", header: "Placement" },
        ];
        const data = resolvedData[category.id] || [];

        return (
          <Box
            key={category.id}
            sx={{
              marginBottom: 4,
              border: "1px solid black",
              borderRadius: 1,
            }}
          >
            <Box sx={{ marginBottom: 0, backgroundColor: "#f5f5f5", padding: 2, borderBottom: "1px solid black" }}>
              <Typography variant="h6">{category.name}</Typography>
              <Typography variant="subtitle1">
                Type: {category.type}, Gender: {category.gender}
              </Typography>
              <Typography variant="subtitle1">
                Enrolled {category.type === "teams" ? "Teams" : "Athletes"}:{" "}
                {category.type === "teams" ? category.teams.length : category.enrolled_athletes.length}
              </Typography>
            </Box>

            <MaterialReactTable
              columns={columns}
              data={data}
              enableColumnFilters={false}
              enableGlobalFilter={false}
              enableColumnOrdering={false}
              enableFullScreenToggle={false}
              enablePagination={false}
              enableSorting={false}
              enableRowActions={false}
              enableDensityToggle={false}
              enableHiding={false}
              enableBottomToolbar={false}
              enableTopToolbar={false}
              enableRowSelection={false}
              enableColumnActions={false}
              muiTableBodyCellProps={({ cell }) => ({
                sx: {
                  fontWeight: cell.column.id === "placement" && cell.getValue()?.includes("Place") ? "bold" : "normal",
                },
              })}
            />
          </Box>
        );
      })}
    </Box>
  );
};

export default CompetitionDetails;