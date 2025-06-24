import { useState } from 'react'
import {Routes, Route} from 'react-router'
import './App.css'
import Home from './components/Dashboard'
import CreateClub from './components/CreateClub'
import Edit from './components/Edit'
import Navbar from './components/navbar/Navbar'
import Clubs from './components/Clubs'
import Dashboard from './components/Dashboard'
import Athletes from './components/Athletes'
import CreateAthlete from './components/CreateAthlete'
import EditAthlete from './components/EditAthlete'
import ViewAthlete from './components/ViewAthlete'
import ViewClub from './components/ViewClub'
import Competitions from './components/Competitions'
import CompetitionDetails from './components/CompetitionDetails'

function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/create-club" element={<CreateClub />} />
      <Route path="/clubs" element={<Clubs />} />
      <Route path="clubs/edit/:id" element={<Edit />} />
      <Route path="/competition/:competitionId" element={<CompetitionDetails />} />
      <Route path="/athletes/" element={<Athletes />} />
      <Route path="/create-athlete" element={<CreateAthlete />} />
      <Route path="/athletes/edit/:id" element={<EditAthlete />} />
      <Route path="/athletes/:id/" element={<ViewAthlete />} />
      <Route path="/clubs/:id" element={<ViewClub />} />
      <Route path="/competitions" element={<Competitions />} />
    </Routes>
  );
}

export default App
