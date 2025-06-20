import React, { useEffect, useState } from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { Typography } from "@mui/material"; // Import Typography
import AxiosInstance from "./Axios";
import { Box } from "@mui/system";

const Competitions = () => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const fetchCompetitionsAndCategories = async () => {
      try {
        // Fetch competitions
        const competitionsResponse = await AxiosInstance.get("competition/");
        const competitionsData = competitionsResponse.data;

        // Fetch all categories
        const categoriesResponse = await AxiosInstance.get("category/");
        const categoriesData = categoriesResponse.data;

        // Fetch all teams
        const teamsResponse = await AxiosInstance.get("team/");
        const teamsData = teamsResponse.data;

        // Create nodes and edges for the mindmap
        const newNodes = [];
        const newEdges = [];

        competitionsData.forEach((competition, compIndex) => {
          // Add a node for the competition
          const competitionNodeId = `competition-${competition.id}`;
          newNodes.push({
            id: competitionNodeId,
            data: { label: `${competition.name} (${competition.place})` },
            position: { x: compIndex * 500, y: 0 }, // Position competitions horizontally
            style: { background: "#1976d2", color: "#fff", padding: 10, borderRadius: 5 },
          });

          // Add nodes and edges for categories
          const competitionCategories = categoriesData.filter(
            (category) => category.competition === competition.id
          );

          competitionCategories.forEach((category, catIndex) => {
            const categoryNodeId = `category-${category.id}`;
            newNodes.push({
              id: categoryNodeId,
              data: { label: `${category.name} (${category.type}, ${category.gender})` },
              position: { x: compIndex * 500 + (catIndex + 1) * 200, y: 150 }, // Position categories horizontally
              style: { background: "#4caf50", color: "#fff", padding: 10, borderRadius: 5 },
            });

            // Connect category to competition
            newEdges.push({
              id: `edge-${competitionNodeId}-${categoryNodeId}`,
              source: competitionNodeId,
              target: categoryNodeId,
              animated: true,
              style: { stroke: "#1976d2" },
            });

            // Add nodes for teams or athletes based on category type
            if (category.type === "teams") {
              // Display only teams for "teams" category type
              category.teams.forEach((teamId, teamIndex) => {
                const team = teamsData.find((team) => team.id === teamId);
                const teamNodeId = `team-${category.id}-${teamId}`;
                const isFirstPlace = category.first_place_team === teamId;
                const isSecondPlace = category.second_place_team === teamId;
                const isThirdPlace = category.third_place_team === teamId;

                newNodes.push({
                  id: teamNodeId,
                  data: {
                    label: isFirstPlace
                      ? `${team?.name || `Team ${teamId}`} 🥇`
                      : isSecondPlace
                      ? `${team?.name || `Team ${teamId}`} 🥈`
                      : isThirdPlace
                      ? `${team?.name || `Team ${teamId}`} 🥉`
                      : `${team?.name || `Team ${teamId}`}`,
                  },
                  position: { x: compIndex * 500 + (catIndex + 1) * 200, y: 300 + teamIndex * 100 },
                  style: {
                    background: isFirstPlace
                      ? "gold"
                      : isSecondPlace
                      ? "silver"
                      : isThirdPlace
                      ? "brown"
                      : "#f5f5f5",
                    color: "#000",
                    padding: 10,
                    borderRadius: 5,
                  },
                });

                // Connect team to category
                newEdges.push({
                  id: `edge-${categoryNodeId}-${teamNodeId}`,
                  source: categoryNodeId,
                  target: teamNodeId,
                  animated: true,
                  style: { stroke: "#4caf50" },
                });
              });
            } else if (category.type === "solo" || category.type === "fight") {
              // Display only athletes for "solo" or "fight" category type
              category.athletes.forEach((athlete, athleteIndex) => {
                const athleteNodeId = `athlete-${category.id}-${athlete.id}`;
                const isFirstPlace = category.first_place === athlete.id;
                const isSecondPlace = category.second_place === athlete.id;
                const isThirdPlace = category.third_place === athlete.id;

                newNodes.push({
                  id: athleteNodeId,
                  data: {
                    label: isFirstPlace
                      ? `${athlete.first_name} ${athlete.last_name} 🥇`
                      : isSecondPlace
                      ? `${athlete.first_name} ${athlete.last_name} 🥈`
                      : isThirdPlace
                      ? `${athlete.first_name} ${athlete.last_name} 🥉`
                      : `${athlete.first_name} ${athlete.last_name}`,
                  },
                  position: { x: compIndex * 500 + (catIndex + 1) * 200, y: 300 + athleteIndex * 100 },
                  style: {
                    background: isFirstPlace
                      ? "gold"
                      : isSecondPlace
                      ? "silver"
                      : isThirdPlace
                      ? "brown"
                      : "#f5f5f5",
                    color: "#000",
                    padding: 10,
                    borderRadius: 5,
                  },
                });

                // Connect athlete to category
                newEdges.push({
                  id: `edge-${categoryNodeId}-${athleteNodeId}`,
                  source: categoryNodeId,
                  target: athleteNodeId,
                  animated: true,
                  style: { stroke: "#4caf50" },
                });
              });
            }
          });
        });

        setNodes(newNodes);
        setEdges(newEdges);
      } catch (error) {
        console.error("Error fetching competitions or categories:", error);
        setErrorMessage("Failed to fetch competitions. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchCompetitionsAndCategories();
  }, []);

  if (loading) {
    return <Typography>Loading competitions...</Typography>;
  }

  if (errorMessage) {
    return <Typography color="error">{errorMessage}</Typography>;
  }

  return (
    <Box sx={{ height: "100vh", width: "100%" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </Box>
  );
};

export default Competitions;