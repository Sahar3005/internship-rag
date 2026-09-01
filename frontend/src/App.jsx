import { useState } from "react";
import {
  LayoutDashboard,
  Sparkles,
  Briefcase,
  User,
  FileText,
  Sun,
  Moon,
  Upload,
  Search,
  MapPin,
  Clock,
  Copy,
  CheckCircle2,
  Send,
  Download,
  Mail,
  Menu,
  X,
  LogOut,
} from "lucide-react";

import "./App.css";

const API_URL =
  "https://internship-rag-2.onrender.com/recommend-resume";

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [coverLetter, setCoverLetter] = useState("");
  const [coverLetterLoading, setCoverLetterLoading] = useState(false);
  const [selectedInternship, setSelectedInternship] = useState(null);

  const [chatMessages, setChatMessages] = useState([
    {
      type: "ai",
      text: "Hi! I'm your AI career assistant. How can I help you today?",
    },
  ]);

  const [chatInput, setChatInput] = useState("");

  // -----------------------------
  // Resume Upload
  // -----------------------------

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setResults([]);
      setError("");
    } else {
      alert("Please upload a PDF resume.");
    }
  };

  // -----------------------------
  // API Call
  // -----------------------------

  const findMatches = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setResults([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to process resume."
        );
      }

      setResults(data.matches || []);

      // Move user to internships page after successful matching
      setActivePage("internships");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const generateCoverLetter = async (internship) => {
    if (!file) {
      setError("Please upload your resume first.");
      setActivePage("dashboard");
      return;
    }

    if (!internship) {
      setError("Please select an internship.");
      return;
    }

    // Save the internship that user clicked
    setSelectedInternship(internship);

    // Open Cover Letter page immediately
    setActivePage("cover-letter");

    // Start loading
    setCoverLetterLoading(true);
    setCoverLetter("");
    setError("");

    const formData = new FormData();

    formData.append("file", file);

    formData.append(
      "internship",
      JSON.stringify(internship)
    );

    try {
      const response = await fetch(
        "https://internship-rag-2.onrender.com/generate-cover-letter",
        {
          method: "POST",
          body: formData,
        }
      );

      // Safely read response
      const contentType = response.headers.get("content-type");

      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();

        throw new Error(
          text || "Server returned an invalid response."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
          data.message ||
          "Failed to generate cover letter."
        );
      }

      const generatedLetter =
        data.cover_letter ||
        data.coverLetter ||
        data.generated_cover_letter ||
        "";

      if (!generatedLetter) {
        throw new Error(
          "Cover letter was not returned by the server."
        );
      }

      setCoverLetter(generatedLetter);

    } catch (err) {
      console.error("Cover Letter Error:", err);

      setError(
        err.message ||
        "Unable to generate cover letter."
      );

    } finally {
      setCoverLetterLoading(false);
    }
  };

  // -----------------------------
  // Navigation
  // -----------------------------

  const navigate = (page) => {
    setActivePage(page);
    setSidebarOpen(false);
  };

  // -----------------------------
  // AI Assistant
  // -----------------------------

  const sendMessage = () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput.trim();

    setChatMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: userMessage,
      },
    ]);

    setChatInput("");

    setTimeout(() => {
      let reply =
        "I can help you with internships, resume improvement, interview preparation and career guidance.";

      const message = userMessage.toLowerCase();

      if (message.includes("resume")) {
        reply =
          "Your resume should highlight Python, AI/ML, SQL, projects and measurable achievements. You can upload your resume in the Dashboard to find matching internships.";
      } else if (message.includes("interview")) {
        reply =
          "For technical interviews, focus on Python, SQL, OOPs, data structures, DBMS, APIs and questions related to your projects.";
      } else if (message.includes("python")) {
        reply =
          "For Python roles, revise functions, OOPs, lists, dictionaries, exception handling, file handling, APIs and popular libraries like Pandas and NumPy.";
      } else if (message.includes("internship")) {
        reply =
          "Your best matches can be found by uploading your resume. The AI will compare your resume with the internship database.";
      }

      setChatMessages((prev) => [
        ...prev,
        {
          type: "ai",
          text: reply,
        },
      ]);
    }, 700);
  };


  // -----------------------------
  // Sidebar Items
  // -----------------------------

  const menuItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      id: "assistant",
      label: "AI Assistant",
      icon: Sparkles,
    },
    {
      id: "internships",
      label: "Internships",
      icon: Briefcase,
    },
    {
      id: "profile",
      label: "Profile",
      icon: User,
    },
    {
      id: "cover-letter",
      label: "Cover Letter",
      icon: FileText,
    },
  ];

  return (
    <div className={darkMode ? "app dark" : "app"}>

      {/* Mobile Header */}

      <div className="mobile-header">
        <button
          className="mobile-menu-btn"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu size={22} />
        </button>

        <div className="mobile-logo">
          InternMatch <span>AI</span>
        </div>
      </div>

      {/* Sidebar Overlay */}

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}

      <aside
        className={
          sidebarOpen
            ? "sidebar sidebar-open"
            : "sidebar"
        }
      >

        <div className="sidebar-top">

          <div className="brand">
            <div className="brand-icon">
              <Sparkles size={21} />
            </div>

            <div>
              <h2>InternMatch</h2>
              <span>AI Career Platform</span>
            </div>
          </div>

          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>

        </div>

        <div className="menu-title">
          MENU
        </div>

        <nav className="sidebar-menu">

          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.id}
                className={
                  activePage === item.id
                    ? "menu-item active"
                    : "menu-item"
                }
                onClick={() => navigate(item.id)}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            );
          })}

        </nav>

        {/* Bottom Sidebar */}

        <div className="sidebar-bottom">

          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? (
              <Sun size={19} />
            ) : (
              <Moon size={19} />
            )}

            <span>
              {darkMode
                ? "Light Mode"
                : "Dark Mode"}
            </span>
          </button>

          <div className="user-mini">

            <div className="avatar">
              SA
            </div>

            <div className="user-mini-info">
              <strong>Sahar Ansari</strong>
              <span>Job Seeker</span>
            </div>

          </div>

        </div>

      </aside>

      {/* Main */}

      <main className="main-content">

        {/* Topbar */}

        <header className="topbar">

          <div>

            <h1>
              {activePage === "dashboard" &&
                "Dashboard"}

              {activePage === "assistant" &&
                "AI Assistant"}

              {activePage === "internships" &&
                "Internships"}

              {activePage === "profile" &&
                "My Profile"}

              {activePage === "cover-letter" &&
                "Cover Letter"}
            </h1>

            <p>
              {activePage === "dashboard" &&
                "Manage your internship search from one place."}

              {activePage === "assistant" &&
                "Get personalized career guidance with AI."}

              {activePage === "internships" &&
                "Explore internships matched to your profile."}

              {activePage === "profile" &&
                "Manage your professional information."}

              {activePage === "cover-letter" &&
                "Create a professional cover letter for applications."}
            </p>

          </div>

          <div className="topbar-profile">

            <div className="top-avatar">
              SA
            </div>

            <div>
              <strong>Sahar Ansari</strong>
              <span>Candidate</span>
            </div>

          </div>

        </header>

        {/* ================= DASHBOARD ================= */}

        {activePage === "dashboard" && (

          <section className="page">

            {/* Welcome Card */}

            <div className="welcome-card">

              <div>

                <span className="welcome-label">
                  WELCOME BACK 👋
                </span>

                <h2>
                  Find your next
                  <span> opportunity.</span>
                </h2>

                <p>
                  Upload your resume and let AI find
                  internships that match your skills.
                </p>

              </div>

              <div className="welcome-icon">
                <Sparkles size={55} />
              </div>

            </div>

            {/* Stats */}

            <div className="stats-grid">

              <div className="stat-card">
                <div className="stat-icon purple">
                  <Briefcase size={21} />
                </div>

                <div>
                  <span>Matches Found</span>
                  <strong>{results.length}</strong>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon green">
                  <CheckCircle2 size={21} />
                </div>

                <div>
                  <span>Resume Status</span>
                  <strong>
                    {file ? "Ready" : "Pending"}
                  </strong>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon blue">
                  <Sparkles size={21} />
                </div>

                <div>
                  <span>AI Matching</span>
                  <strong>Active</strong>
                </div>
              </div>

            </div>

            {/* Upload */}

            <div className="dashboard-grid">

              <div className="upload-card">

                <div className="card-heading">

                  <div>
                    <h3>Upload Resume</h3>
                    <p>
                      Upload your latest PDF resume.
                    </p>
                  </div>

                  <FileText size={23} />

                </div>

                <input
                  type="file"
                  id="resume"
                  accept=".pdf"
                  onChange={handleFileChange}
                  hidden
                />

                <label
                  htmlFor="resume"
                  className="dashboard-upload"
                >

                  <div className="upload-round">
                    <Upload size={25} />
                  </div>

                  {file ? (
                    <>
                      <strong>{file.name}</strong>
                      <span>
                        Resume selected successfully
                      </span>
                    </>
                  ) : (
                    <>
                      <strong>
                        Drop your resume here
                      </strong>

                      <span>
                        or click to browse PDF files
                      </span>
                    </>
                  )}

                </label>

                <button
                  className="primary-btn full"
                  disabled={!file || loading}
                  onClick={findMatches}
                >
                  <Search size={18} />

                  {loading
                    ? "Analyzing Resume..."
                    : "Find Matching Internships"}
                </button>

                {error && (
                  <div className="error-box">
                    {error}
                  </div>
                )}

              </div>

              {/* How it works */}

              <div className="steps-card">

                <div className="card-heading">

                  <div>
                    <h3>How It Works</h3>
                    <p>
                      Three simple steps.
                    </p>
                  </div>

                  <Sparkles size={23} />

                </div>

                <div className="steps">

                  <div className="step">
                    <div className="step-number">
                      01
                    </div>

                    <div>
                      <strong>
                        Upload Resume
                      </strong>

                      <p>
                        Upload your latest PDF resume.
                      </p>
                    </div>
                  </div>

                  <div className="step">
                    <div className="step-number">
                      02
                    </div>

                    <div>
                      <strong>
                        AI Analysis
                      </strong>

                      <p>
                        AI extracts your skills and experience.
                      </p>
                    </div>
                  </div>

                  <div className="step">
                    <div className="step-number">
                      03
                    </div>

                    <div>
                      <strong>
                        Get Matches
                      </strong>

                      <p>
                        Receive ranked internship recommendations.
                      </p>
                    </div>
                  </div>

                </div>

              </div>

            </div>

            {/* Recent Matches */}

            {results.length > 0 && (

              <div className="recent-section">

                <div className="section-title">

                  <div>
                    <span>AI RESULTS</span>
                    <h2>
                      Top Matches
                    </h2>
                  </div>

                  <button
                    className="text-btn"
                    onClick={() =>
                      navigate("internships")
                    }
                  >
                    View all →
                  </button>

                </div>

                <div className="mini-results">

                  {results.slice(0, 3).map((internship) => (

                    <div
                      className="mini-card"
                      key={
                        internship.internship_id
                      }
                    >

                      <div className="company-logo">
                        {internship.company
                          ?.substring(0, 2)
                          .toUpperCase()}
                      </div>

                      <div className="mini-info">

                        <h3>
                          {internship.title}
                        </h3>

                        <p>
                          {internship.company}
                        </p>

                      </div>

                      <span className="match-score">
                        {internship.similarity_score}%
                      </span>

                    </div>

                  ))}

                </div>

              </div>

            )}

          </section>

        )}

        {/* ================= AI ASSISTANT ================= */}

        {activePage === "assistant" && (

          <section className="page">

            <div className="assistant-container">

              <div className="assistant-header">

                <div className="assistant-avatar">
                  <Sparkles size={27} />
                </div>

                <div>
                  <h2>
                    AI Career Assistant
                  </h2>

                  <p>
                    Ask anything about your career,
                    internships or interviews.
                  </p>
                </div>

                <span className="online-badge">
                  ● Online
                </span>

              </div>

              <div className="chat-area">

                {chatMessages.map(
                  (message, index) => (

                    <div
                      key={index}
                      className={
                        message.type === "user"
                          ? "chat-message user-message"
                          : "chat-message ai-message"
                      }
                    >

                      {message.type === "ai" && (
                        <div className="chat-icon">
                          <Sparkles size={16} />
                        </div>
                      )}

                      <div className="message-bubble">
                        {message.text}
                      </div>

                    </div>

                  )
                )}

              </div>

              <div className="suggestions">

                <button
                  onClick={() =>
                    setChatInput(
                      "How can I improve my resume?"
                    )
                  }
                >
                  Improve my resume
                </button>

                <button
                  onClick={() =>
                    setChatInput(
                      "How should I prepare for interviews?"
                    )
                  }
                >
                  Interview preparation
                </button>

                <button
                  onClick={() =>
                    setChatInput(
                      "Which internship is best for me?"
                    )
                  }
                >
                  Find best internship
                </button>

              </div>

              <div className="chat-input">

                <input
                  value={chatInput}
                  onChange={(e) =>
                    setChatInput(e.target.value)
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      sendMessage();
                    }
                  }}
                  placeholder="Ask your career question..."
                />

                <button onClick={sendMessage}>
                  <Send size={18} />
                </button>

              </div>

            </div>

          </section>

        )}

        {/* ================= INTERNSHIPS ================= */}

        {activePage === "internships" && (

          <section className="page">

            <div className="internship-page-header">

              <div>
                <span className="small-label">
                  AI MATCH RESULTS
                </span>

                <h2>
                  Recommended Internships
                </h2>

                <p>
                  {results.length > 0
                    ? `Found ${results.length} internships matched to your resume.`
                    : "Upload your resume from the Dashboard to get personalized matches."}
                </p>
              </div>

              <button
                className="primary-btn"
                onClick={() =>
                  navigate("dashboard")
                }
              >
                <Upload size={18} />
                Upload Resume
              </button>

            </div>

            {results.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  <Briefcase size={32} />
                </div>

                <h3>
                  No internships yet
                </h3>

                <p>
                  Upload your resume to let our AI
                  find the best opportunities for you.
                </p>

                <button
                  className="primary-btn"
                  onClick={() =>
                    navigate("dashboard")
                  }
                >
                  Upload Resume
                </button>

              </div>

            ) : (

              <div className="internship-grid">

                {results.map((internship) => (

                  <div
                    className="internship-card"
                    key={
                      internship.internship_id ||
                      internship.rank
                    }
                  >

                    <div className="card-top">

                      <div className="company-logo">
                        {internship.company
                          ?.substring(0, 2)
                          .toUpperCase()}
                      </div>

                      <span className="match-score">
                        {internship.similarity_score}%
                        Match
                      </span>

                    </div>

                    <h3>
                      {internship.title}
                    </h3>

                    <p className="company-name">
                      {internship.company}
                    </p>

                    <div className="details">

                      <span>
                        <MapPin size={16} />
                        {internship.location}
                      </span>

                      <span>
                        <Briefcase size={16} />
                        {internship.work_mode}
                      </span>

                      <span>
                        <Clock size={16} />
                        {internship.duration}
                      </span>

                    </div>

                    <p className="description">
                      {internship.description}
                    </p>

                    <div className="skills">

                      {internship.required_skills
                        ?.slice(0, 5)
                        .map(
                          (skill, index) => (
                            <span key={index}>
                              {skill}
                            </span>
                          )
                        )}

                    </div>

                    <div className="card-actions">

                      <button
                        className="cover-letter-btn"
                        onClick={() => generateCoverLetter(internship)}
                        disabled={coverLetterLoading}
                      >
                        <Mail size={17} />

                        {coverLetterLoading &&
                          selectedInternship?.internship_id === internship.internship_id
                          ? "Generating..."
                          : "Generate Cover Letter"}
                      </button>

                      <button
                        className="apply-btn"
                        onClick={() => {
                          alert(`Apply for ${internship.title}`);
                        }}
                      >
                        Apply Now
                      </button>

                    </div>

                  </div>

                ))}

              </div>

            )}

          </section>

        )}

        {/* ================= PROFILE ================= */}

        {activePage === "profile" && (

          <section className="page">

            <div className="profile-layout">

              <div className="profile-card">

                <div className="large-avatar">
                  SA
                </div>

                <h2>
                  Sahar Ansari
                </h2>

                <p>
                  Computer Science & AI/ML
                </p>

                <span className="profile-status">
                  Open to Opportunities
                </span>

              </div>

              <div className="profile-details">

                <div className="detail-card">

                  <h3>
                    Education
                  </h3>

                  <div className="profile-row">
                    <div>
                      <strong>
                        B.Tech Computer Science
                      </strong>

                      <span>
                        AI & Machine Learning
                      </span>
                    </div>

                    <span>
                      2026
                    </span>
                  </div>

                </div>

                <div className="detail-card">

                  <h3>
                    Technical Skills
                  </h3>

                  <div className="profile-skills">

                    {[
                      "Python",
                      "Machine Learning",
                      "SQL",
                      "Pandas",
                      "NumPy",
                      "Power BI",
                      "Django",
                      "FastAPI",
                      "Git & GitHub",
                      "RAG",
                      "FAISS",
                      "AI",
                    ].map(
                      (skill) => (
                        <span key={skill}>
                          {skill}
                        </span>
                      )
                    )}

                  </div>

                </div>

                <div className="detail-card">

                  <h3>
                    Projects
                  </h3>

                  <div className="project-list">

                    <div>
                      <strong>
                        Internship RAG Pipeline
                      </strong>

                      <p>
                        AI-powered internship
                        recommendation system using
                        resume embeddings and vector search.
                      </p>
                    </div>

                    <div>
                      <strong>
                        Breast Cancer Detection
                      </strong>

                      <p>
                        Machine learning based medical
                        diagnosis project.
                      </p>
                    </div>

                    <div>
                      <strong>
                        Smart Attendance System
                      </strong>

                      <p>
                        Face recognition based attendance
                        application.
                      </p>
                    </div>

                  </div>

                </div>

              </div>

            </div>

          </section>

        )}

        {/* ================= COVER LETTER ================= */}

        {activePage === "cover-letter" && (
          <section className="page">

            <div className="cover-letter-page">

              {/* Header */}
              <div className="cover-header">

                <div>
                  <span className="small-label">
                    AI WRITING TOOL
                  </span>

                  <h2>
                    Cover Letter Generator
                  </h2>

                  <p>
                    Create a personalized cover letter for your
                    selected internship.
                  </p>
                </div>

                <button
                  className="primary-btn"
                  disabled={
                    !selectedInternship ||
                    coverLetterLoading
                  }
                  onClick={() =>
                    generateCoverLetter(selectedInternship)
                  }
                >
                  <Sparkles size={18} />

                  {coverLetterLoading
                    ? "Generating..."
                    : "Generate Cover Letter"}
                </button>

              </div>


              {/* Selected Internship */}
              {selectedInternship && (

                <div className="selected-internship-card">

                  <div className="selected-company-logo">
                    {selectedInternship.company
                      ?.substring(0, 2)
                      .toUpperCase()}
                  </div>

                  <div className="selected-internship-info">

                    <span>
                      COVER LETTER FOR
                    </span>

                    <h3>
                      {selectedInternship.title}
                    </h3>

                    <p>
                      {selectedInternship.company}
                    </p>

                  </div>

                  <div className="selected-match">

                    {selectedInternship.similarity_score}%

                    <span>
                      Match
                    </span>

                  </div>

                </div>

              )}


              {/* Error */}
              {error && (
                <div className="error-box">
                  {error}
                </div>
              )}


              {/* No Internship */}
              {!selectedInternship && (

                <div className="cover-empty">

                  <div className="cover-empty-icon">
                    <FileText size={28} />
                  </div>

                  <h3>
                    No internship selected
                  </h3>

                  <p>
                    Go to the Internships page and click
                    "Generate Cover Letter" for the internship
                    you want to apply for.
                  </p>

                  <button
                    className="primary-btn"
                    onClick={() =>
                      navigate("internships")
                    }
                  >
                    <Briefcase size={18} />
                    View Internships
                  </button>

                </div>

              )}


              {/* Cover Letter Document */}
              {selectedInternship && (

                <div className="cover-document">

                  {/* Document Header */}
                  <div className="document-top">

                    <div>

                      <span>
                        PERSONALIZED APPLICATION
                      </span>

                      <h3>
                        Cover Letter
                      </h3>

                    </div>

                    <FileText size={20} />

                  </div>


                  {/* Loading */}
                  {coverLetterLoading ? (

                    <div className="cover-loading">

                      <div className="loading-icon">
                        <Sparkles size={25} />
                      </div>

                      <h3>
                        Creating your cover letter...
                      </h3>

                      <p>
                        AI is tailoring your resume and skills
                        to this internship.
                      </p>

                    </div>

                  ) : (

                    <textarea
                      className="cover-letter-textarea"
                      value={coverLetter}
                      onChange={(e) =>
                        setCoverLetter(e.target.value)
                      }
                      placeholder="Your personalized cover letter will appear here..."
                    />

                  )}


                  {/* Actions */}
                  {coverLetter &&
                    !coverLetterLoading && (

                      <div className="cover-actions">

                        <button
                          className="secondary-btn"
                          onClick={() => {
                            navigator.clipboard.writeText(
                              coverLetter
                            );
                          }}
                        >
                          <Copy size={17} />
                          Copy Letter
                        </button>


                        <button
                          className="primary-btn"
                          onClick={() => {

                            const blob = new Blob(
                              [coverLetter],
                              {
                                type: "text/plain",
                              }
                            );

                            const url =
                              URL.createObjectURL(blob);

                            const a =
                              document.createElement("a");

                            a.href = url;

                            a.download =
                              `${selectedInternship.title
                                ?.replace(
                                  /[^a-z0-9]/gi,
                                  "-"
                                )
                                .toLowerCase()}-cover-letter.txt`;

                            document.body.appendChild(a);

                            a.click();

                            document.body.removeChild(a);

                            URL.revokeObjectURL(url);

                          }}
                        >
                          <Download size={17} />
                          Download
                        </button>

                      </div>

                    )}

                </div>

              )}

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;