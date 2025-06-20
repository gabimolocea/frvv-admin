{activeTab === 5 && (
  <>
    {/* Matches Section */}
    <TableContainer component={Paper} sx={{ border: "1px solid #ccc", overflow: "hidden" }}>
      <Table sx={{ width: "100%", tableLayout: "fixed" }} aria-label="matches table">
        <TableHead>
          <TableRow>
            <TableCell sx={{ width: "33%", fontWeight: "bold", wordWrap: "break-word" }}>Match Name</TableCell>
            <TableCell sx={{ width: "33%", fontWeight: "bold", wordWrap: "break-word" }}>Category</TableCell>
            <TableCell sx={{ width: "33%", fontWeight: "bold", wordWrap: "break-word" }}>Winner</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {relatedData?.matches?.length > 0 ? (
            relatedData.matches.map((match, index) => (
              <TableRow key={index}>
                <TableCell sx={{ wordWrap: "break-word" }}>{match?.name || "N/A"}</TableCell>
                <TableCell sx={{ wordWrap: "break-word" }}>{match?.category_name || "N/A"}</TableCell>
                <TableCell sx={{ wordWrap: "break-word" }}>
                  {match?.winner_name === athleteData?.first_name ? (
                    <Typography sx={{ color: "green", fontWeight: "bold" }}>
                      {match?.winner_name} (Winner 🏆)
                    </Typography>
                  ) : (
                    match?.winner_name || "N/A"
                  )}
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} align="center">
                No matches found for this athlete.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  </>
)}