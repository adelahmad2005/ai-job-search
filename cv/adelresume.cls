% adelresume.cls - one-page ATS-friendly resume class for Adel Abdelmoaty.
% Replicates documents/cv/Adel_Abdelmoaty_Resume_*.pdf: Lato, single column,
% uppercase section headings over a full-width rule, bold title + italic
% company on the left, "dates | location" on the right, tight bullets.
% Compile with lualatex (fontspec). HARD LIMIT: exactly 1 page.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{adelresume}[2026/09/26 One-page resume]
\LoadClass[10pt]{article}

\RequirePackage[a4paper,left=12.5mm,right=12.5mm,top=9mm,bottom=9mm]{geometry}
\RequirePackage{fontspec}
\RequirePackage{enumitem}
\RequirePackage{xcolor}
\RequirePackage[hidelinks]{hyperref}

\setmainfont{Lato}[
  Path = ./fonts/lato/,
  Extension = .ttf,
  UprightFont = *-Reg,
  BoldFont = *-Bol,
  ItalicFont = *-RegIta,
  BoldItalicFont = *-BolIta
]
\hypersetup{pdfauthor={Adel Abdelmoaty}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\raggedbottom
% Body 9.5pt like the Word original.
\renewcommand\normalsize{\fontsize{9.5}{11.4}\selectfont}
\normalsize
% No automatic hyphenation: a word split across lines ("predic-tive")
% can break ATS keyword matching. Explicit hyphens still break.
\hyphenpenalty=10000
\exhyphenpenalty=50
\emergencystretch=2em
% Left-aligned, not justified: justification squeezes interword spaces and
% text extractors (ATS) then merge words ("seven AI" -> "sevenAI").
\AtBeginDocument{\raggedright}

% Bullets: tight, small indent, round bullet like the Word original.
\setlist[itemize]{label=\textbullet, leftmargin=12pt, labelsep=5pt,
  itemsep=0.6pt, parsep=0pt, topsep=1pt, partopsep=0pt}

% \resumename{ADEL ABDELMOATY}
\newcommand{\resumename}[1]{{\fontsize{20}{22}\selectfont\bfseries #1\par}\vspace{2pt}}
% \contactline{text} - one contact line, small
\newcommand{\contactline}[1]{{\fontsize{8.5}{10.5}\selectfont #1\par}}

% \resumesection{SUMMARY}
\newcommand{\resumesection}[1]{%
  \vspace{4pt}%
  {\fontsize{10.5}{12}\selectfont\bfseries\MakeUppercase{#1}\par}%
  \vspace{0.5pt}\hrule height 0.6pt\vspace{2pt}}

% \entry{Title}{Company}{Dates}{Location}
\newcommand{\entry}[4]{%
  \vspace{2pt}%
  {\textbf{#1}, \textit{#2}\hfill #3\ifx&#4&\else\ \ |\ \ #4\fi\par}}

% \skillline{Label}{items}
\newcommand{\skillline}[2]{{\textbf{#1:} #2\par}}
