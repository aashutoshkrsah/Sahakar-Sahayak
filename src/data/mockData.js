// Mock Database for Sahakar Sahayak

export const cooperativeGuideCategories = [
  {
    id: "getting-started",
    title: "Getting Started",
    icon: "BookOpen",
    description: "Learn what cooperatives are, their core philosophy, and foundational rules.",
    articles: [
      {
        id: "what-is-cooperative",
        title: "What is a Cooperative?",
        content: "A cooperative is an autonomous association of persons united voluntarily to meet their common economic, social, and cultural needs and aspirations through a jointly-owned and democratically-controlled enterprise. Unlike traditional corporations, cooperatives are value-driven, focusing on community benefit rather than purely maximizing shareholder value.",
        sections: [
          { subtitle: "Core Definition", text: "Cooperatives are business organizations owned and operated by a group of individuals for their mutual benefit." },
          { subtitle: "Key Features", text: "1. Democratic management (one member, one vote).\n2. Member ownership of shares.\n3. Surplus distributed based on usage, not just investment capital.\n4. Dual identity: members are both users and owners of the business." }
        ]
      },
      {
        id: "types-of-cooperatives",
        title: "Types of Cooperatives",
        content: "Cooperatives can be formed in various sectors depending on their members' needs. Common classifications include:",
        sections: [
          { subtitle: "1. Financial / Savings & Credit", text: "Commonly known as SACCOs (Savings and Credit Cooperatives). They provide financial intermediation, offering savings accounts and credit access to members at reasonable rates." },
          { subtitle: "2. Agricultural Cooperatives", text: "Help farmers pool resources for purchasing seeds, fertilizer, and equipment, and jointly processing or marketing their agricultural yields." },
          { subtitle: "3. Consumer Cooperatives", text: "Owned by consumers who buy goods (like groceries or household items) in bulk to distribute to members at fair prices." },
          { subtitle: "4. Producer / Multi-purpose Cooperatives", text: "Enable small producers or multiple objectives to operate jointly, enhancing scale and reducing transaction costs." }
        ]
      },
      {
        id: "cooperative-principles",
        title: "The 7 Cooperative Principles",
        content: "The Rochdale Principles define the operational ethics of cooperatives globally, adopted by the International Co-operative Alliance (ICA):",
        sections: [
          { subtitle: "1. Voluntary and Open Membership", text: "Cooperatives are voluntary organizations, open to all persons able to use their services and willing to accept the responsibilities of membership." },
          { subtitle: "2. Democratic Member Control", text: "Controlled by their members, who actively participate in setting policies and making decisions. One person, one vote." },
          { subtitle: "3. Member Economic Participation", text: "Members contribute equitably to, and democratically control, the capital of their cooperative." },
          { subtitle: "4. Autonomy and Independence", text: "Self-help organizations controlled by their members." },
          { subtitle: "5. Education, Training, and Information", text: "Cooperatives provide education and training for their members, elected representatives, managers, and employees so they can contribute effectively to development." },
          { subtitle: "6. Cooperation among Cooperatives", text: "Cooperatives serve their members most effectively and strengthen the cooperative movement by working together." },
          { subtitle: "7. Concern for Community", text: "Cooperatives work for the sustainable development of their communities through policies approved by their members." }
        ]
      }
    ]
  },
  {
    id: "registration",
    title: "Registration",
    icon: "FilePlus",
    description: "Guidance on requirements, document filing, and registration office workflows.",
    articles: [
      {
        id: "eligibility-req",
        title: "Registration Eligibility Requirements",
        content: "Before applying to register a cooperative, ensure you meet the minimum statutory criteria under the Cooperative Laws:",
        sections: [
          { subtitle: "Membership Minimums", text: "A minimum of 25 individuals from separate families is generally required to form a primary cooperative. Some specific types, like multi-purpose or agricultural, might require more based on provincial guidelines." },
          { subtitle: "Geographical Restraints", text: "Members must reside or work within the proposed operating area of the cooperative (common bond of association)." },
          { subtitle: "Capital Accumulation", text: "Members must pledge to purchase at least one share. Initial capital must be deposited in a designated bank account once approval is initiated." }
        ]
      },
      {
        id: "reg-step-by-step",
        title: "Step-by-Step Registration Process",
        content: "Here is the standard procedure to register a cooperative entity:",
        sections: [
          { subtitle: "Step 1: Preliminary Meeting", text: "Hold an ad-hoc meeting of promoters. Draft a resolution to establish the cooperative, select an ad-hoc committee (usually 3-5 members), and agree on the name and area of operation." },
          { subtitle: "Step 2: Bylaws Drafting", text: "Draft the cooperative's bylaws (Vidhan). This document defines the name, address, objectives, share value, membership criteria, and governance structure." },
          { subtitle: "Step 3: Feasibility Report", text: "Prepare a simple 3-year financial feasibility report outlining source of funds, operating expenses, and projected growth." },
          { subtitle: "Step 4: Submission", text: "Submit the physical or digital application to the local Registrar or Cooperative Division of your municipality." },
          { subtitle: "Step 5: Review & Approval", text: "The registry reviews the documents. If correct, you will receive a Registration Certificate and a Tax registration (PAN)." }
        ]
      }
    ]
  },
  {
    id: "membership",
    title: "Membership",
    icon: "Users",
    description: "Explore member rights, duties, capital subscriptions, and termination rules.",
    articles: [
      {
        id: "member-rights",
        title: "Rights of a Cooperative Member",
        content: "Members are the ultimate owners. Their legal rights include:",
        sections: [
          { subtitle: "Governance Rights", text: "1. Right to attend, speak, and vote at the General Assembly.\n2. Right to contest elections for the Board of Directors or Accounts Committee.\n3. Right to requisition a Special General Assembly as per bylaws." },
          { subtitle: "Economic Rights", text: "1. Right to receive services provided by the cooperative (loans, purchase rebates, marketing services).\n2. Right to receive dividends (patronage refund and interest on share capital) from net savings.\n3. Right to withdraw membership and claim share capital refund as per rules." }
        ]
      },
      {
        id: "member-duties",
        title: "Responsibilities of Members",
        content: "Active participation is vital for cooperative survival. Member duties include:",
        sections: [
          { subtitle: "Commitments", text: "1. Respecting and abiding by the cooperative bylaws and resolutions.\n2. Utilizing the cooperative services regularly (patronizing the business).\n3. Paying share calls and interest/loan installments on time.\n4. Attending annual meetings to supervise management." }
        ]
      }
    ]
  },
  {
    id: "governance",
    title: "Governance",
    icon: "ShieldAlert",
    description: "General Assembly protocols, board elections, and supervisory committees.",
    articles: [
      {
        id: "general-assembly",
        title: "The General Assembly (AGM)",
        content: "The General Assembly (annual general meeting of all members) is the supreme authority of the cooperative.",
        sections: [
          { subtitle: "Powers & Functions", text: "1. Approving annual budgets, plans, and audit reports.\n2. Electing and removing Board Directors and Internal Audit Committee members.\n3. Amending the bylaws.\n4. Deciding on mergers, divisions, or liquidation.\n5. Setting maximum debt limits." },
          { subtitle: "Quorum", text: "Usually, more than 50% of the total active members must be present to form a quorum for the AGM. If the quorum is not met, a rescheduled meeting can be held with a lower threshold as defined by regulation (often 33% or 40%)." }
        ]
      },
      {
        id: "board-of-directors",
        title: "Board of Directors and Officers",
        content: "The Board of Directors (Sanchalak Samiti) manages the day-to-day operations and executes general assembly resolutions.",
        sections: [
          { subtitle: "Composition", text: "Consists of an odd number of directors (typically 5, 7, 9, or 11). Includes a Chairperson, Vice-Chairperson, Secretary, and Treasurer. At least 33% female representation is mandated under modern acts." },
          { subtitle: "Term of Office", text: "Board terms generally range between 3 to 5 years, subject to reelection guidelines in the bylaws." }
        ]
      }
    ]
  },
  {
    id: "financial-management",
    title: "Financial Management",
    icon: "TrendingUp",
    description: "Understanding share capital, reserve funds, and statutory internal/external audits.",
    articles: [
      {
        id: "share-capital",
        title: "Understanding Share Capital",
        content: "Share capital represents the equity contribution of members. Unlike corporate stock, cooperative shares do not trade on public exchanges, do not appreciate in value, and have strict ownership caps (e.g. no single member can own more than 20% of total shares to prevent consolidation).",
        sections: [
          { subtitle: "Reserve Funds", text: "Every year, a portion of the net savings (usually 25%) must be transferred to a mandatory Cooperative Reserve Fund before distributing any dividends. This ensures financial stability." }
        ]
      },
      {
        id: "audit-req",
        title: "Audit Requirements",
        content: "Audit is a legal obligation to ensure transparency and prevent financial fraud.",
        sections: [
          { subtitle: "Types of Audit", text: "1. Internal Audit: Performed by an elected internal accounts committee to monitor transactions quarterly.\n2. Statutory External Audit: Conducted annually by a registered auditor approved by the Cooperative Registrar. The audit report must be submitted to the General Assembly and the regulatory authority within 6 months of the fiscal year-end." }
        ]
      }
    ]
  },
  {
    id: "dispute-resolution",
    title: "Dispute Resolution",
    icon: "Scale",
    description: "Resolving member conflicts, committee deadlocks, and filing regulatory complaints.",
    articles: [
      {
        id: "common-disputes",
        title: "Common Cooperative Disputes",
        content: "Disputes can arise between members, between members and the committee, or between cooperatives. Typical conflicts include:",
        sections: [
          { subtitle: "Categories of Disputes", text: "1. Loan defaults and recovery issues.\n2. Disagreement over committee election processes or votes.\n3. Accusations of financial mismanagement or board nepotism.\n4. Arbitrary cancellation of membership." }
        ]
      },
      {
        id: "resolution-mechanisms",
        title: "How to Resolve Disputes",
        content: "Cooperative laws prioritize peaceful, out-of-court settlements:",
        sections: [
          { subtitle: "1. Internal Mediation", text: "Attempt to settle via the internal sub-committee or cooperative's own arbitration panel." },
          { subtitle: "2. Referral to the Registrar", text: "If internal resolution fails, write a formal complaint to the local Registrar of Cooperatives. The Registrar has the authority to hear disputes, order inquiries, and direct arbitration." },
          { subtitle: "3. Arbitration", text: "Appointed arbitrators hear both parties. Their award has the same enforcement force as a civil court decree." }
        ]
      }
    ]
  }
];

export const legalResources = [
  {
    id: "cooperative-act-2074",
    title: "Cooperative Act, 2074 (2017)",
    description: "The primary legislative act governing the establishment, operation, regulation, and facilitation of cooperative societies in Nepal.",
    category: "Laws",
    lastUpdated: "2024-03-12",
    overview: "This Act replaces the old Cooperative Act of 2048 to streamline cooperative governance, decentralize regulatory powers to local municipalities, enforce stricter penalty guidelines on savings cooperatives, and establish credit information centers and cooperative tribunals.",
    content: `
      <h3>Chapter 1: Preliminary</h3>
      <p>Defines cooperative values, principles, and key terms like "Registrar", "Operating Area", "Primary Cooperative", and "Cooperative Union".</p>
      
      <h3>Chapter 2: Registration & Incorporation</h3>
      <p>Section 3: Any group of at least 25 individuals from separate families can establish a primary cooperative society.</p>
      <p>Section 4: Application must be submitted along with proposed bylaws, feasibility plan, and membership list.</p>
      
      <h3>Chapter 3: Membership</h3>
      <p>Section 24: Eligibility. Any citizen residing in the operating area who is willing to buy shares and accept bylaws can become a member.</p>
      <p>Section 30: Voting. One member, one vote. Proxies are strictly prohibited except in cooperative unions.</p>
      
      <h3>Chapter 4: Capital & Financial Provisions</h3>
      <p>Section 67: Share capital cannot be consolidated by single members beyond 20%.</p>
      <p>Section 68: Net savings must allocate 25% to the Reserve Fund, 15% to Cooperative Promotion Fund, and others before dividends.</p>
    `,
    relatedTopics: ["Cooperative Registration", "Democratic Governance", "Reserve Funds"],
    downloadUrl: "#"
  },
  {
    id: "cooperative-rules-2076",
    title: "Cooperative Regulations, 2076 (2019)",
    description: "Detailed operational regulations and procedures implementing the provisions of the Cooperative Act, 2074.",
    category: "Regulations",
    lastUpdated: "2025-01-20",
    overview: "Provides granular rules regarding cooperative registration fees, format of bylaws, financial ratios, liquidity requirements, board meetings, election procedures, and registration of cooperative unions and federations.",
    content: `
      <h3>Rule 5: Bylaws Details</h3>
      <p>Specifies 28 distinct elements that must be listed in a cooperative's bylaws, including share value, loan rules, savings interest limits, and staff hiring procedures.</p>
      
      <h3>Rule 18: Interest Rate Spread</h3>
      <p>Restricts the interest rate spread (difference between loan interest and savings interest) in financial cooperatives to a maximum of 6% to prevent usurious practices.</p>
      
      <h3>Rule 42: AGM Notices</h3>
      <p>Mandates that notice for the Annual General Meeting (AGM) must be published in a public newspaper or distributed to members at least 15 days in advance, accompanied by the audited financial statements.</p>
    `,
    relatedTopics: ["AGM Protocol", "Interest Rate Spread", "Bylaws Template"],
    downloadUrl: "#"
  },
  {
    id: "sacco-liquidity-guideline",
    title: "SACCO Liquidity & Safety Guidelines, 2080",
    description: "Regulatory guidelines outlining financial safety ratios, capital adequacy, and liquidity limits for financial cooperatives.",
    category: "Guidelines",
    lastUpdated: "2025-08-15",
    overview: "Issued by the Department of Cooperatives to address liquidity crunches, these guidelines enforce capital ratios, pearl ratios, and mandatory cash reserve requirements for savings and credit cooperatives.",
    content: `
      <h3>Section 2: Cash Reserve Ratio (CRR)</h3>
      <p>All savings cooperatives must maintain at least 10% of their total savings deposits as liquid assets (cash in vault or bank balance) at all times.</p>
      
      <h3>Section 5: Capital Adequacy</h3>
      <p>Cooperatives must maintain institutional capital of not less than 5% of their total asset value to absorb unexpected financial shocks.</p>
      
      <h3>Section 8: Single Obligor Limit</h3>
      <p>No cooperative shall extend credit to a single member exceeding 10% of its total capital fund, reducing concentration risk.</p>
    `,
    relatedTopics: ["Financial Audit", "Capital Adequacy", "Liquidity Management"],
    downloadUrl: "#"
  },
  {
    id: "coop-merger-policy-2081",
    title: "Cooperative Merger & Acquisition Policy Guideline, 2081",
    description: "Guidelines and procedures for merging two or more cooperatives to consolidate resources and enhance efficiency.",
    category: "Policies",
    lastUpdated: "2026-05-10",
    overview: "Facilitates cooperative consolidation by offering tax incentives, simplifying asset valuation processes, and protecting member capital during mergers.",
    content: `
      <h3>Chapter 2: Proposal and Resolution</h3>
      <p>Both cooperatives must approve a merger proposal in their respective General Assemblies with a 2/3 majority vote.</p>
      
      <h3>Chapter 4: Asset-Liability Valuation (DDA)</h3>
      <p>Mandates appointing an independent auditor to perform a Due Diligence Audit (DDA) to determine share exchange ratios and reconcile bad loans.</p>
    `,
    relatedTopics: ["Merger", "Due Diligence", "Bylaw Amendment"],
    downloadUrl: "#"
  },
  {
    id: "coop-taxation-manual",
    title: "Cooperative Taxation Directives, 2079",
    description: "Comprehensive manual explaining Tax deductions, VAT exemptions, and Income tax rates for cooperatives depending on location.",
    category: "Regulations",
    lastUpdated: "2023-11-05",
    overview: "Clarifies taxation structures. Primary agricultural cooperatives are often fully exempt, while savings cooperatives pay lower corporate taxes (5% to 20%) depending on municipal location.",
    content: `
      <h3>Section 4: Tax Exemption Criteria</h3>
      <p>Cooperatives engaged in farming, seeds, dairy, and cold storage are 100% exempt from income tax on transactions with members.</p>
      
      <h3>Section 6: Tax Rates</h3>
      <p>Financial cooperatives in metropolitan areas are subject to a 10% corporate income tax, sub-metropolitan 7%, and rural municipalities 5%.</p>
    `,
    relatedTopics: ["Taxation", "VAT Exemption", "Municipal Rules"],
    downloadUrl: "#"
  }
];

export const documentGuidanceData = [
  {
    id: "cooperative-registration",
    title: "Cooperative Registration",
    description: "Initial steps and documents required to register a brand-new cooperative society.",
    checklist: [
      { id: "reg-1", name: "Application Form", desc: "Standard registration application addressed to the Registrar, signed by all ad-hoc committee members.", required: true },
      { id: "reg-2", name: "Proposed Bylaws (Vidhan)", desc: "Two signed copies of the bylaws detailing name, rules, operating area, share capital value, and internal structures.", required: true },
      { id: "reg-3", name: "Feasibility Study Report", desc: "A 3-year projected business plan showing financial viability, market analysis, and social impact objectives.", required: true },
      { id: "reg-4", name: "Identification Documents", desc: "Certified copies of citizenship cards and photos of at least 25 promoting members.", required: true },
      { id: "reg-5", name: "Minutes of Promoters Meeting", desc: "Official minutes showing selection of the ad-hoc board, approval of bylaws, and resolution to register.", required: true },
      { id: "reg-6", name: "Operating Office Proof", desc: "House rent agreement or land ownership document for the proposed registered office.", required: false }
    ]
  },
  {
    id: "membership-application",
    title: "Membership Application",
    description: "Process and forms required for an individual to join an existing cooperative.",
    checklist: [
      { id: "mem-1", name: "Membership Application Form", desc: "Formal request detailing applicant's address, occupation, and agreement to follow bylaws.", required: true },
      { id: "mem-2", name: "Citizenship Certificate copy", desc: "Proof of nationality and age (applicant must be at least 18 years old).", required: true },
      { id: "mem-3", name: "Passport-size photographs", desc: "Two recent photos for the membership register and identity card.", required: true },
      { id: "mem-4", name: "Share Capital Subscription", desc: "Receipt of payment for purchasing the minimum shares (e.g. 1 share worth 1,000 Nrs).", required: true },
      { id: "mem-5", name: "Entrance Fee Receipt", desc: "Receipt for a non-refundable entry registration fee specified in bylaws.", required: true }
    ]
  },
  {
    id: "committee-formation",
    title: "Committee Formation & Election",
    description: "Documents required to report a newly elected Board of Directors or Accounts Committee.",
    checklist: [
      { id: "com-1", name: "AGM Election Minutes", desc: "Minutes of the General Assembly meeting detailing the election process, nominees, and vote count.", required: true },
      { id: "com-2", name: "Oath of Office Form", desc: "Signed oath of secrecy and fiduciary duty forms for all newly elected directors.", required: true },
      { id: "com-3", name: "List of Elected Members", desc: "Detailed list with names, designations, emails, contact info, and signatures of the board.", required: true },
      { id: "com-4", name: "Internal Audit Report", desc: "Prior committee's audit clearance or handover document.", required: false },
      { id: "com-5", name: "Bio-Data Forms", desc: "Brief educational and professional profiles of the directors.", required: false }
    ]
  },
  {
    id: "annual-reporting",
    title: "Annual Reporting & Compliance",
    description: "Submitting periodic operational reports to the regulatory municipality or department.",
    checklist: [
      { id: "rep-1", name: "Annual Progress Report", desc: "Operational review highlighting members added, meetings held, and training conducted, signed by the chairperson.", required: true },
      { id: "rep-2", name: "Audited Financial Statements", desc: "Balance sheet, income statement, cash flow, and note disclosures prepared by a certified auditor.", required: true },
      { id: "rep-3", name: "AGM Decisions Minutes", desc: "Approved resolutions of the AGM, including dividend allocation approvals.", required: true },
      { id: "rep-4", name: "Internal Accounts Committee Report", desc: "Annual oversight report presented by the Internal Audit Committee.", required: true }
    ]
  },
  {
    id: "audit-filing",
    title: "Audit Submission",
    description: "Filing your annual statutory audit details with the Registrar's office.",
    checklist: [
      { id: "aud-1", name: "Auditor Appointment Letter", desc: "Board or AGM resolution nominating the registered auditor.", required: true },
      { id: "aud-2", name: "Complete Audit Report", desc: "Full booklet with auditor's opinion, cash verifications, and compliance checklists.", required: true },
      { id: "aud-3", name: "Management Letter Responses", desc: "Board's official reply to any financial flags or errors raised by the auditor.", required: true },
      { id: "aud-4", name: "Tax Clearance Certificate", desc: "Proof of filing municipal taxes and TDS payments.", required: false }
    ]
  },
  {
    id: "dispute-complaint",
    title: "Complaint / Dispute Filing",
    description: "Filing a formal complaint to the Registrar or internal dispute committee.",
    checklist: [
      { id: "dis-1", name: "Formal Complaint Letter", desc: "Detailed timeline of the grievance, names of parties involved, and the remedy requested.", required: true },
      { id: "dis-2", name: "Supporting Evidence Documents", desc: "Ledgers, emails, receipt copies, or meeting minutes proving the dispute claims.", required: true },
      { id: "dis-3", name: "Share/Membership Proof", desc: "Copy of applicant's share certificate or passbook proving standing in the cooperative.", required: true },
      { id: "dis-4", name: "Internal Mediation Attempts proof", desc: "Minutes showing internal dispute resolutions were attempted but failed.", required: false }
    ]
  }
];

export const faqData = [
  {
    question: "How do I ask Sahayak a question?",
    answer: "Go to the 'Ask Sahayak' page from the sidebar. Type your question in natural language (English, Nepali, or Hindi) in the input box at the bottom, and press Enter or click the Send button. Sahayak will provide a detailed, structured response."
  },
  {
    question: "Can I use the app without logging in?",
    answer: "Yes! You can select 'Continue as Guest' on the login screen. Guests have access to the Cooperative Guide, Legal Resources, and can ask Sahayak questions. However, guests cannot save answers, view chat history, or edit a profile."
  },
  {
    question: "How do I switch the language?",
    answer: "You can change the language at any time. A language selector dropdown is available in the top navbar, on the Landing page, on the chatbot screen, and in the Settings page. Choosing Hindi or Nepali will translate the UI labels and options."
  },
  {
    question: "How do I bookmark/save an answer?",
    answer: "In the chatbot conversation, you can click the bookmark/star icon on any answer card. This saves the answer to your 'Saved Answers' page, which you can search and filter later. This feature requires you to be logged in."
  },
  {
    question: "Is the advice provided by Sahayak legally binding?",
    answer: "No. As shown in our disclaimer, Sahakar Sahayak provides informational guidance to help users navigate rules. It does not replace formal legal advice from qualified attorneys or competent cooperative registration officers."
  }
];
