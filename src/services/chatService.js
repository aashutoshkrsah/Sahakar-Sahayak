// Chat Service simulating future API integration
// Future Endpoint: POST /api/chat
// Payload: { "message": "...", "language": "en", "conversationId": "..." }

export const chatService = {
  sendMessage: (messageText, language = 'en', conversationId = null) => {
    console.log(`[API Mock Call] POST /api/chat`);
    console.log(`Payload:`, { message: messageText, language, conversationId });

    return new Promise((resolve) => {
      // Simulate network latency (1.2 seconds)
      setTimeout(() => {
        const query = messageText.toLowerCase();
        let response = {
          answer: "",
          steps: [],
          notes: [],
          provisions: [],
          documents: [],
          sources: [],
          suggestedQuestions: []
        };

        // 1. REGISTRATION CATEGORY
        if (
          query.includes('register') || 
          query.includes('registration') || 
          query.includes('दर्ता') || 
          query.includes('ನೋಂದಣಿ') || 
          query.includes('ನೊಂದಣಿ') ||
          query.includes('ಮಾದೋದು ಹೇಗೆ')
        ) {
          if (language === 'kn') {
            response.answer = "ಸಹಕಾರ ಸಂಘವನ್ನು ನೋಂದಾಯಿಸಲು ಈ ಕೆಳಗಿನ ಹಂತಗಳನ್ನು ಮತ್ತು ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಒದಗಿಸಬೇಕಾಗುತ್ತದೆ:";
            response.steps = [
              "ಕನಿಷ್ಠ 25 ಪ್ರವರ್ತಕ ಸದಸ್ಯರ (ವಿವಿಧ ಕುಟುಂಬಗಳಿಂದ) ಸಭೆಯನ್ನು ಕರೆದು ಪ್ರವರ್ತಕ ಸಮಿತಿಯನ್ನು ರಚಿಸುವುದು.",
              "ಸಂಘದ ಉಪನಿಯಮಗಳು (Vidhan / ಬೈಲಾಗಳು) ಮತ್ತು 3 ವರ್ಷಗಳ ಕಾರ್ಯಸಾಧ್ಯತಾ ಯೋಜನೆ ವರದಿಯನ್ನು ಸಿದ್ಧಪಡಿಸುವುದು.",
              "ನೋಂದಣಿ ಅಧಿಕಾರಿಗಳು ಅಥವಾ ಸ್ಥಳೀಯ ಮುನ್ಸಿಪಾಲಿಟಿಯ ಸಹಕಾರ ವಿಭಾಗಕ್ಕೆ ಅರ್ಜಿಯನ್ನು ಸಲ್ಲಿಸುವುದು.",
              "ಪರಿಶೀಲನೆಯ ನಂತರ ನೋಂದಣಿ ಪ್ರಮಾಣಪತ್ರ ಮತ್ತು ಪ್ಯಾನ್ (PAN) ಸಂಖ್ಯೆಯನ್ನು ಪಡೆಯುವುದು."
            ];
            response.notes = ["ಗಮನಿಸಿ: ಒಂದೇ ಕುಟುಂಬದ ಒಂದಕ್ಕಿಂತ ಹೆಚ್ಚು ವ್ಯಕ್ತಿಗಳು ಪ್ರಾಥಮಿಕ ಸಹಕಾರ ಸಂಘದ ಸದಸ್ಯರಾಗಲು ಅವಕಾಶವಿಲ್ಲ."];
            response.provisions = ["ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 4 (ನೋಂದಣಿ ನಿಯಮಗಳು)"];
            response.documents = ["ನೋಂದಣಿ ಅರ್ಜಿ ನಮೂನೆ", "ಪ್ರಸ್ತಾವಿತ ಬೈಲಾಗಳು (2 ಪ್ರತಿಗಳು)", "ಕಾರ್ಯಸಾಧ್ಯತಾ ಯೋಜನೆ ವರದಿ", "25 ಸದಸ್ಯರ ಗುರುತಿನ ಚೀಟಿ ಪ್ರತಿಗಳು", "ಪ್ರವರ್ತಕರ ಸಭೆಯ ನಡಾವಳಿ ಪುಸ್ತಕ"];
            response.sources = [
              { documentName: "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆ", provision: "ಸೆಕ್ಷನ್ 4: ನೋಂದಣಿ ಅರ್ಜಿ", id: "cooperative-act-2074" },
              { documentName: "ಸಹಕಾರ ನಿಯಮಾವಳಿಗಳು", provision: "ರೂಲ್ 3: ನೋಂದಣಿ ಹಂತಗಳು", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "ನೋಂದಣಿ ಶುಲ್ಕ ಎಷ್ಟು?",
              "ಕನಿಷ್ಠ ಪಾಲು ಬಂಡವಾಳ (Share Capital) ಎಷ್ಟು ಇರಬೇಕು?",
              "ಮಾದರಿ ಉಪನಿಯಮಗಳು ಎಲ್ಲಿ ದೊರೆಯುತ್ತವೆ?"
            ];
          } else if (language === 'ne') {
            response.answer = "सहकारी संस्था दर्ता गर्नका लागि देहाय बमोजिमको प्रक्रिया र कागजातहरू पुरा करनाुपर्दछ:";
            response.steps = [
              "प्रवर्द्धकहरूको भेला गरी कम्तीमा २५ जना सदस्यहरूको तदर्थ समिति चयन गर्ने।",
              "संस्थाको विनियम (नियमावली) र ३ वर्षे कार्ययोजना मस्यौदा तयार गर्ने।",
              "स्थानीय तह वा सहकारी विभागमा आवश्यक कागजातहरू सहित निवेदन पेश गर्ने।",
              "स्वीकृति पश्चात् स्थायी लेखा नम्बर (PAN) र संस्था दर्ता प्रमाणपत्र प्राप्त गर्ने।"
            ];
            response.notes = ["संस्था दर्ता गर्दा एकै परिवारका सदस्यहरू छुट्टाछुट्टै सदस्य हुनु हुँदैन ।"];
            response.provisions = ["सहकारी ऐन, २०७४ को दफा ३ र ४ दर्ता प्रक्रिया सम्बन्धी व्यवस्था"];
            response.documents = ["दर्ता निवेदन पत्र", "प्रस्तावित विनियम (२ प्रति)", "सम्भाव्यता अध्ययन प्रतिवेदन", "२५ सदस्यहरूको नागरिकता प्रतिलिपि", "तदर्थ समितिको निर्णय प्रतिलिपि"];
            response.sources = [
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ४: दर्ताको लागि निवेदन", id: "cooperative-act-2074" },
              { documentName: "सहकारी नियमावली, २०७६", provision: "नियम ३: दर्ता सम्बन्धी प्रक्रिया", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "दर्ता शुल्क कति लाग्छ?",
              "न्यूनतम शेयर पूँजी कति चाहिन्छ?",
              "विनियमको ढाँचा कहाँ पाइन्छ?"
            ];
          } else if (language === 'hi') {
            response.answer = "सहकारी समिति के पंजीकरण के लिए निम्नलिखित प्रक्रिया और आवश्यक दस्तावेज पूरे करने होंगे:";
            response.steps = [
              "प्रमोटरों की बैठक आयोजित कर कम से कम 25 सदस्यों की एक तदर्थ समिति का गठन करें।",
              "सहकारी समिति के उपनियम (Vidhan) और 3 वर्ष की व्यवहार्यता रिपोर्ट तैयार करें।",
              "संबंधित रजिस्ट्रार या स्थानीय निकाय के सहकारी प्रभाग में आवेदन पत्र जमा करें।",
              "सत्यापन के बाद, आपको पंजीकरण प्रमाणपत्र और पैन (PAN) नंबर प्राप्त होगा।"
            ];
            response.notes = ["ध्यान दें कि एक ही परिवार से केवल एक सदस्य ही प्राथमिक सहकारी का हिस्सा हो सकता है।"];
            response.provisions = ["सहकारी अधिनियम, 2074 की धारा 3 और 4"];
            response.documents = ["पंजीकरण आवेदन पत्र", "प्रस्तावित उपनियम (2 प्रतियां)", "व्यवहार्यता रिपोर्ट", "25 प्रमोटर सदस्यों के पहचान पत्र", "तदर्थ समिति की बैठक के कार्यवृत्त"];
            response.sources = [
              { documentName: "सहकारी अधिनियम, 2074", provision: "धारा 4: पंजीकरण के लिए आवेदन", id: "cooperative-act-2074" },
              { documentName: "सहकारी नियम, 2076", provision: "नियम 3: पंजीकरण प्रक्रिया", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "पंजीकरण में कितना समय लगता है?",
              "न्यूनतम शेयर पूंजी कितनी होनी चाहिए?",
              "उपनियमों को कैसे संशोधित किया जाता है?"
            ];
          } else {
            response.answer = "To register a cooperative society, you need to follow a structured legal process and compile the necessary documentation:";
            response.steps = [
              "Gather a minimum of 25 individuals from separate families to hold a preliminary meeting and form an ad-hoc promoter committee.",
              "Draft the cooperative bylaws (Vidhan) and a 3-year viability feasibility report.",
              "Submit the formal application along with promoter credentials to the local municipality registrar's office.",
              "Upon review and approval, receive your Registration Certificate and apply for a Tax Identification Number (PAN)."
            ];
            response.notes = ["Important: Members must fall under the same geographical area of operation as specified in the proposed bylaws."];
            response.provisions = ["Section 3 & 4 of the Cooperative Act, 2074 ( Nepal )"];
            response.documents = ["Application Form for Registration", "Two copies of Proposed Bylaws", "3-Year Feasibility Report", "Certified copies of citizenship for all 25+ members", "Minutes of the promoters meeting"];
            response.sources = [
              { documentName: "Cooperative Act, 2074", provision: "Section 4: Application for Registration", id: "cooperative-act-2074" },
              { documentName: "Cooperative Regulations, 2076", provision: "Rule 3: Registration Procedures", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "What is the cost of cooperative registration?",
              "What is the minimum share capital required?",
              "Where can I find a model bylaws draft?"
            ];
          }
        } 
        
        // 2. MEMBER RIGHTS CATEGORY
        else if (
          query.includes('member') || 
          query.includes('rights') || 
          query.includes('ಸದಸ್ಯ') || 
          query.includes('ಹಕ್ಕುಗಳು') || 
          query.includes('ಹಕ್ಕು') || 
          query.includes('सदस्य') || 
          query.includes('अधिकार')
        ) {
          if (language === 'kn') {
            response.answer = "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆಯಡಿ ಸದಸ್ಯರಿಗೆ ಈ ಕೆಳಗಿನ ಹಕ್ಕುಗಳು ಮತ್ತು ಜವಾಬ್ದಾರಿಗಳಿವೆ:";
            response.steps = [
              "ಪ್ರಜಾಪ್ರಭುತ್ವದ ನಿಯಂತ್ರಣ: ಪ್ರತಿಯೊಬ್ಬ ಸದಸ್ಯನಿಗೆ ಒಂದು ಮತದ ಹಕ್ಕಿರುತ್ತದೆ (ಒಬ್ಬ ಸದಸ್ಯ, ಒಂದು ಮತ).",
              "ಚುನಾವಣೆಯಲ್ಲಿ ಸ್ಪರ್ಧೆ: ಆಡಳಿತ ಮಂಡಳಿ ಅಥವಾ ಲೆಕ್ಕಪರಿಶೋಧನಾ ಸಮಿತಿ ಚುನಾವಣೆಗೆ ಸ್ಪರ್ಧಿಸುವ ಹಕ್ಕು.",
              "ಲಾಭಾಂಶದ ಹಕ್ಕು: ಸಂಘದ ಸೇವೆಗಳನ್ನು ಪಡೆಯುವುದು ಮತ್ತು ಉಳಿತಾಯದ ಮೇಲಿನ ಲಾಭಾಂಶವನ್ನು ಹೊಂದುವ ಹಕ್ಕು."
            ];
            response.notes = ["ಗಮನಿಸಿ: ಸಹಕಾರ ಸಂಘದಲ್ಲಿ ಪ್ರಾತಿನಿಧಿಕ (Proxy) ಮತದಾನಕ್ಕೆ ಅವಕಾಶವಿರುವುದಿಲ್ಲ. ಸದಸ್ಯರೇ ಖುದ್ದಾಗಿ ಭಾಗವಹಿಸಬೇಕು."];
            response.provisions = ["ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 30 ಮತ್ತು 34"];
            response.documents = ["ಸದಸ್ಯತ್ವ ಅರ್ಜಿ", "ಪಾಲು ಬಂಡವಾಳ ಪುಸ್ತಕ (Share Passbook)"];
            response.sources = [
              { documentName: "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆ", provision: "ಸೆಕ್ಷನ್ 34: ಸದಸ್ಯರ ಹಕ್ಕುಗಳು", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ಸದಸ್ಯತ್ವವನ್ನು ಹೇಗೆ ರದ್ದುಗೊಳಿಸಬಹುದು?",
              "ಸದಸ್ಯರ ಜವಾಬ್ದಾರಿಗಳು ಏನೇನು?",
              "ಒಬ್ಬ ವ್ಯಕ್ತಿ ಎಷ್ಟು ಪಾಲು ಹೊಂದಬಹುದು?"
            ];
          } else if (language === 'ne') {
            response.answer = "सहकारी ऐन अनुसार सहकारीका सदस्यहरूलाई देहाय बमोजिमका अधिकार र कर्तव्यहरू प्राप्त छन्:";
            response.steps = [
              "प्रजातान्त्रिक सहभागिता: साधारण सभामा उपस्थित भई छलफल गर्ने र मत (एक सदस्य, एक मत) हाल्ने अधिकार।",
              "उम्मेदवारी अधिकार: सञ्चालक समिति वा लेखा समितिमा निर्वाचित हुन वा मतदान गर्न पाउने अधिकार।",
              "आर्थिक लाभ: सहकारीको सेवा उपयोग गरे बापत संरक्षण कोष फिर्ता (Patronage refund) र शेयरमा लाभांश पाउने अधिकार।"
            ];
            response.notes = ["शेयर पूँजी जतिसुकै भए पनि एक सदस्यले एक मत मात्र दिन पाउनेछ, प्रोक्सी मतदान पाइने छैन।"];
            response.provisions = ["सहकारी ऐन, २०७४ को दफा ३० (मतदान अधिकार) र दफा ३४ (सदस्यको अधिकार)"];
            response.documents = ["सदस्यता निवेदन फारम", "शेयर प्रमाणपत्र / पासबुक"];
            response.sources = [
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ३०: मतदान सम्बन्धी व्यवस्था", id: "cooperative-act-2074" },
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ३४: सदस्यहरूको अधिकार", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "सहकारीको सदस्यता कसरी त्याग्न सकिन्छ?",
              "के एक व्यक्ति दुईवटा सहकारीको सदस्य बन्न पाउँछ?",
              "शेयर रकम कसरी फिर्ता पाइन्छ?"
            ];
          } else if (language === 'hi') {
            response.answer = "सहकारी नियमों के अनुसार एक सदस्य को निम्नलिखित अधिकार और जिम्मेदारियां प्राप्त होती हैं:";
            response.steps = [
              "लोकतांत्रिक नियंत्रण: प्रत्येक सदस्य को साधारण सभा में वोट देने का अधिकार है (एक सदस्य, एक वोट)।",
              "चुनाव में सहभागिता: निदेशक मंडल (Board) या आंतरिक ऑडिट समिति के चुनाव में खड़े होने और मतदान करने का अधिकार।",
              "आर्थिक लाभांश: सहकारी द्वारा प्रदान की जाने वाली सुविधाओं का उपयोग करने और मुनाफे में से लाभांश प्राप्त करने का अधिकार।"
            ];
            response.notes = ["ध्यान दें: सहकारी में प्रोक्सी (Proxy) वोटिंग मान्य नहीं है। सदस्य को स्वयं उपस्थित होना होगा।"];
            response.provisions = ["सहकारी अधिनियम, 2074 की धारा 30 और 34"];
            response.documents = ["सदस्यता शेयर प्रमाण पत्र", "सदस्य पासबुक"];
            response.sources = [
              { documentName: "सहकारी अधिनियम, 2074", provision: "धारा 34: सदस्य के अधिकार", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "क्या सदस्यता रद्द की जा सकती है?",
              "एक सहकारी सदस्य की क्या जिम्मेदारियां होती हैं?",
              "शेयर लाभांश की अधिकतम सीमा क्या है?"
            ];
          } else {
            response.answer = "Cooperatives are democratic associations. Under the Cooperative Laws, members possess specific rights and obligations:";
            response.steps = [
              "Democratic Participation: Every member holds exactly one vote in the General Assembly, regardless of their shareholdings (One Member, One Vote).",
              "Right to Contest: Members can stand as nominees for the Board of Directors or Audit Committee, subject to bylaws eligibility.",
              "Economic returns: Accessing cooperative services, receiving patronage refunds based on transactions, and earning interest/dividends on shares."
            ];
            response.notes = ["Note: Proxy voting is strictly prohibited. Members must physically or virtually attend meetings to exercise votes."];
            response.provisions = ["Section 30 (Voting Rights) and Section 34 (Rights of Members) of the Cooperative Act, 2074"];
            response.documents = ["Membership Application Form", "Share Passbook", "Cooperative Identity Card"];
            response.sources = [
              { documentName: "Cooperative Act, 2074", provision: "Section 30: Voting Provisions", id: "cooperative-act-2074" },
              { documentName: "Cooperative Act, 2074", provision: "Section 34: Member Entitlements", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "How can cooperative membership be terminated?",
              "Can a member own more than 20% of cooperative shares?",
              "What happens to member shares if the cooperative merges?"
            ];
          }
        } 
        
        // 3. COMMITTEE / MANAGEMENT CATEGORY
        else if (
          query.includes('committee') || 
          query.includes('management') || 
          query.includes('ಸಮಿತಿ') || 
          query.includes('ಆಡಳಿತ') || 
          query.includes('समिति') || 
          query.includes('गठन')
        ) {
          if (language === 'kn') {
            response.answer = "ಸಹಕಾರ ಸಂಘದ ಆಡಳಿತ ಮಂಡಳಿ (Board of Directors) ರಚನೆ ಮತ್ತು ನಿಯಮಾವಳಿಗಳು ಕೆಳಗಿನಂತಿವೆ:";
            response.steps = [
              "ಆಡಳಿತ ಮಂಡಳಿಯ ಸದಸ್ಯರನ್ನು ವಾರ್ಷಿಕ ಮಹಾಸಭೆಯ (AGM) ಮೂಲಕ ಪ್ರಜಾಸತ್ತಾತ್ಮಕವಾಗಿ ಆರಿಸಲಾಗುತ್ತದೆ.",
              "ಮಂಡಳಿಯ ಸದಸ್ಯರ ಸಂಖ್ಯೆ ಬೆಸ ಸಂಖ್ಯೆಯಾಗಿರಬೇಕು (ಉದಾಹರಣೆಗೆ 5, 7, 9 ಅಥವಾ 11 ಸದಸ್ಯರು).",
              "ಕಾನೂನಿನ ಪ್ರಕಾರ ಮಂಡಳಿಯಲ್ಲಿ ಕನಿಷ್ಠ ಶೇಕಡಾ 33 ರಷ್ಟು ಮಹಿಳಾ ಪ್ರಾತಿನಿಧ್ಯ ಇರಬೇಕು."
            ];
            response.notes = ["ಆಡಳಿತ ಮಂಡಳಿಯ ಅವಧಿಯು ಸಾಮಾನ್ಯವಾಗಿ 3 ರಿಂದ 5 ವರ್ಷಗಳಾಗಿದ್ದು, ಉಪನಿಯಮದಲ್ಲಿ ನಿರ್ದಿಷ್ಟಪಡಿಸಿದಂತೆ ಇರುತ್ತದೆ."];
            response.provisions = ["ಸಹಕಾರ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 41"];
            response.documents = ["ಚುನಾವಣಾ ನಡಾವಳಿ ದಾಖಲೆ", "ಸದಸ್ಯರ ಪ್ರಮಾಣವಚನ ನಮೂನೆ"];
            response.sources = [
              { documentName: "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆ", provision: "ಸೆಕ್ಷನ್ 41: ಆಡಳಿತ ಮಂಡಳಿ", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ಆಂತರಿಕ ಲೆಕ್ಕಪರಿಶೋಧನಾ ಸಮಿತಿ ಎಂದರೇನು?",
              "ನಿರ್ದೇಶಕರಾಗಲು ಇರುವ ಅರ್ಹತೆಗಳೇನು?",
              "ಮಂಡಳಿ ಸಭೆ ಎಷ್ಟು ದಿನಗಳಿಗೊಮ್ಮೆ ನಡೆಯಬೇಕು?"
            ];
          } else if (language === 'ne') {
            response.answer = "सहकारीको सञ्चालक समिति (Board of Directors) गठन र व्यवस्थापन सम्बन्धी कानूनी प्रावधानहरू निम्न अनुसार छन्:";
            response.steps = [
              "साधारण सभाले निर्वाचन प्रक्रिया मार्फत सञ्चालक समितिको निर्वाचन गर्नेछ।",
              "समितिको आकार बिजोर संख्यामा हुनुपर्दछ (जस्तै ५, ७, ९ वा ११ सदस्य)।",
              "नयाँ ऐन अनुसार समितिमा कम्तीमा ३३ प्रतिशत महिला प्रतिनिधित्व अनिवार्य गरिएको छ।"
            ];
            response.notes = ["सञ्चालक समितिको कार्यकाल सामान्यतया ३ देखि ५ वर्षको हुन्छ र यो विनियममा उल्लेख भए बमोजिम हुन्छ।"];
            response.provisions = ["सहकारी ऐन, २०७४ को दफा ४१ (सञ्चालक समिति गठन)"];
            response.documents = ["निर्वाचन सम्बन्धी निर्णय पुस्तिका", "सञ्चालकहरूको सपथ ग्रहण फारम"];
            response.sources = [
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ४१: समिति गठन", id: "cooperative-act-2074" },
              { documentName: "सहकारी नियमावली, २०७६", provision: "नियम २२: सञ्चालकको योग्यता", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "लेखा सुपरिवेक्षण समिति कसरी गठन हुन्छ?",
              "सञ्चालक हुनका लागि के-कस्ता योग्यताहरू चाहिन्छ?",
              "समितिको बैठक कति समयमा बस्नुपर्छ?"
            ];
          } else if (language === 'hi') {
            response.answer = "सहकारी समिति के प्रबंधन और निदेशक मंडल (Board) के गठन के संबंध में निम्नलिखित प्रावधान हैं:";
            response.steps = [
              "निदेशक मंडल का चुनाव वार्षिक साधारण सभा (AGM) में लोकतांत्रिक तरीके से किया जाता है।",
              "समिति में सदस्यों की संख्या विषम (Odd Number) होनी चाहिए, जैसे 5, 7, 9 या 11 सदस्य।",
              "नियमों के अनुसार निदेशक मंडल में कम से कम 33% महिला प्रतिनिधित्व होना अनिवार्य है।"
            ];
            response.notes = ["समिति का कार्यकाल आमतौर पर 3 से 5 साल तक होता है, जो कि उपनियम में तय होता है।"];
            response.provisions = ["सहकारी अधिनियम, 2074 की धारा 41 (निदेशक मंडल का गठन)"];
            response.documents = ["चुनाव कार्यवृत्त (Election Minutes)", "निदेशकों के शपथ पत्र"];
            response.sources = [
              { documentName: "सहकारी अधिनियम, 2074", provision: "धारा 41: संचालक समिति", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ऑडिट समिति के क्या कार्य हैं?",
              "संचालक मंडल के सदस्यों की अयोग्यताएं क्या हैं?",
              "क्या प्रबंधन समिति को बर्खास्त किया जा सकता है?"
            ];
          } else {
            response.answer = "The Board of Directors (Management Committee) is responsible for implementing AGM resolutions. Its formation parameters include:";
            response.steps = [
              "Election: Directors are elected by members during the General Assembly through secret ballot or consensus.",
              "Odd Number: The committee must comprise an odd number of members (typically 5, 7, 9, or 11) to avoid voting deadlocks.",
              "Gender Inclusion: Under current regulations, a minimum of 33% (one-third) of the board seats must be reserved for female members."
            ];
            response.notes = ["The term of office is specified in the bylaws, usually ranging from 3 to 5 years. Re-election parameters also apply."];
            response.provisions = ["Section 41 of the Cooperative Act, 2074"];
            response.documents = ["Minutes of AGM elections", "Oath of Office signed forms", "List of elected board directors with portfolios"];
            response.sources = [
              { documentName: "Cooperative Act, 2074", provision: "Section 41: Board of Directors", id: "cooperative-act-2074" },
              { documentName: "Cooperative Regulations, 2076", provision: "Rule 22: Director Qualifications", id: "cooperative-rules-2076" }
            ];
            response.suggestedQuestions = [
              "How is the Internal Audit Committee formed?",
              "What are the disqualification criteria for board members?",
              "How often must board meetings be held?"
            ];
          }
        } 
        
        // 4. DISPUTE RESOLUTION CATEGORY
        else if (
          query.includes('dispute') || 
          query.includes('resolution') || 
          query.includes('ವಿವಾದ') || 
          query.includes('ಪರಿಹಾರ') || 
          query.includes('विवाद') || 
          query.includes('समाधान')
        ) {
          if (language === 'kn') {
            response.answer = "ಸಹಕಾರ ಸಂಘಗಳಲ್ಲಿನ ಭಿನ್ನಾಭಿಪ್ರಾಯಗಳು ಮತ್ತು ವಿವಾದಗಳ ಇತ್ಯರ್ಥಕ್ಕೆ ಕೆಳಗಿನ ಕಾನೂನಾತ್ಮಕ ವ್ಯವಸ್ಥೆಗಳಿವೆ:";
            response.steps = [
              "ಆಂತರಿಕ ಸಂಧಾನ: ಮೊದಲು ಸಂಘದ ಆಂತರಿಕ ದೂರು ಅಥವಾ ಸಂಧಾನ ಸಮಿತಿಯ ಮೂಲಕ ಬಗೆಹರಿಸಲು ಪ್ರಯತ್ನಿಸುವುದು.",
              "ಸಹಕಾರ ನಿಬಂಧಕರಿಗೆ ದೂರು: ಆಂತರಿಕವಾಗಿ ಬಗೆಹರಿಯದಿದ್ದರೆ ಸ್ಥಳೀಯ ಸಹಕಾರ ನಿಬಂಧಕರಿಗೆ (Registrar) ಲಿಖಿತ ದೂರು ಸಲ್ಲಿಸುವುದು.",
              "ಸಹಕಾರ ನ್ಯಾಯಮಂಡಳಿ: ಹಣಕಾಸಿನ ವಂಚನೆ ಅಥವಾ ದೊಡ್ಡ ವಿವಾದಗಳ ವಿಚಾರಣೆಯನ್ನು ಸಹಕಾರ ಟ್ರಿಬ್ಯೂನಲ್ (Tribunal) ನಡೆಸುತ್ತದೆ."
            ];
            response.notes = ["ಸಾಲ ಮರುಪಾವತಿ ವಂಚನೆ ಮತ್ತು ಠೇವಣಿ ವಿವಾದಗಳನ್ನು ನಿಬಂಧಕರ ನೇತೃತ್ವದ ನ್ಯಾಯಾಲಯದಲ್ಲಿ ಮೊದಲಿಗೆ ದಾಖಲಿಸಬೇಕು."];
            response.provisions = ["ಸಹಕಾರ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 98"];
            response.documents = ["ಲಿಖಿತ ದೂರು ಅರ್ಜಿ", "ಹಣಕಾಸು ವಹಿವಾಟು ಪುರಾವೆ ದಾಖಲೆಗಳು"];
            response.sources = [
              { documentName: "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆ", provision: "ಸೆಕ್ಷನ್ 98: ವಿವಾದಗಳ ಇತ್ಯರ್ಥ", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ಸಹಕಾರ ರಿಜಿಸ್ಟ್ರಾರ್ ಪಾತ್ರವೇನು?",
              "ಠೇವಣಿ ಹಣ ಮರುಪಾವತಿಯಾಗದಿದ್ದರೆ ಏನು ಮಾಡಬೇಕು?",
              "ಸಾಲ ವಸೂಲಾತಿ ನಿಯಮಗಳೇನು?"
            ];
          } else if (language === 'ne') {
            response.answer = "सहकारीमा देखिने विवादहरूको समाधानका लागि कानूनी रूपमा देहायका व्यवस्थाहरू गरिएका छन्:";
            response.steps = [
              "आन्तरिक समाधान: विवादलाई पहिले सहकारीको आफ्नै उप-समिति वा विवाद समाधान संयन्त्र मार्फत सुल्झाउने प्रयास गर्ने।",
              "रजिष्ट्रार कहाँ निवेदन: आन्तरिक रूपमा समाधान नभएमा सम्बन्धित स्थानीय तह वा सहकारी रजिष्ट्रार समक्ष लिखित निवेदन दिने।",
              "मध्यस्थता/न्यायाधिकरण: रजिष्ट्रारले तोकेको मध्यस्थकर्ता वा सहकारी न्यायाधिकरण मार्फत विवादको निरुपण गर्ने।"
            ];
            response.notes = ["सहकारीको बचत फिर्ता नभएको, ऋण असुली वा चुनावी विवादहरू यस अन्तर्गत पर्दछन्।"];
            response.provisions = ["सहकारी ऐन, २०७४ को दफा ९८ (विवाद समाधान) र दफा ११६ (सहकारी न्यायाधिकरण)"];
            response.documents = ["लिखित उजुरी पत्र", "विवाद सम्बन्धी प्रमाणहरू (रसिद, निर्णय प्रतिलिपि आदि)"];
            response.sources = [
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ९८: विवादको निरुपण", id: "cooperative-act-2074" },
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ११६: सहकारी न्यायाधिकरण", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "सहकारी न्यायाधिकरण भनेको के हो?",
              "ऋण नतिर्ने सदस्य विरुद्ध कसरी कारबाही हुन्छ?",
              "बचतकर्ताको पैसा फिर्ता नभए कहाँ उजुरी गर्ने?"
            ];
          } else if (language === 'hi') {
            response.answer = "सहकारी समिति के विवादों के निपटारे के लिए कानूनी रूप से निम्नलिखित प्रक्रिया अपनाई जाती है:";
            response.steps = [
              "आंतरिक मध्यस्थता: पहले विवाद को सहकारी की अपनी आंतरिक शिकायत समिति के पास ले जाएं।",
              "रजिस्ट्रार को शिकायत: यदि आंतरिक स्तर पर विवाद हल नहीं होता है, तो सहकारी रजिस्ट्रार के पास लिखित शिकायत दर्ज करें।",
              "सहकारी न्यायाधिकरण: वित्तीय गबन या बड़े मुकदमों के लिए सहकारी न्यायाधिकरण (Tribunal) अंतिम सुनवाई करता है।"
            ];
            response.notes = ["ऋण वसूली और बचत वापस न मिलने से संबंधित विवाद रजिस्ट्रार द्वारा मध्यस्थता के लिए भेजे जाते हैं।"];
            response.provisions = ["सहकारी अधिनियम, 2074 की धारा 98 (विवाद समाधान)"];
            response.documents = ["लिखित शिकायत पत्र", "वित्तीय लेनदेन के प्रमाण, पासबुक", "मध्यस्थता अनुरोध पत्र"];
            response.sources = [
              { documentName: "सहकारी अधिनियम, 2074", provision: "धारा 98: विवादों का निपटारा", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "सहकारी न्यायाधिकरण के अधिकार क्या हैं?",
              "डिफॉल्टर सदस्य से ऋण वसूली कैसे की जाती है?",
              "यदि बोर्ड गबन करता है तो शिकायत कहां करें?"
            ];
          } else {
            response.answer = "Cooperative disputes are handled through dedicated administrative and legal channels to ensure rapid resolution:";
            response.steps = [
              "Internal Conciliation: Try to resolve the dispute internally using the cooperative's designated Sub-Committee or Arbitration Panel.",
              "Municipal/Registrar Complaints: If unresolved, escalate the dispute by submitting a formal complaint to the local municipal Cooperative Desk or the Registrar of Cooperatives.",
              "Arbitration / Cooperative Tribunal: The Registrar can refer matters to formal arbitrators. For major financial claims or liquidation disputes, the Cooperative Tribunal oversees the legal adjudication."
            ];
            response.notes = ["Note: Section 98 specifies that disputes concerning election validity, loan recovery, or capital distribution should go to the Registrar before civil courts."];
            response.provisions = ["Section 98 (Dispute Settlement) and Section 116 (Cooperative Tribunal) of the Cooperative Act, 2074"];
            response.documents = ["Written Complaint Application", "Ledger statement or transaction slips proving the dispute", "Minutes showing failure of internal mediation"];
            response.sources = [
              { documentName: "Cooperative Act, 2074", provision: "Section 98: Settlement of Disputes", id: "cooperative-act-2074" },
              { documentName: "Cooperative Act, 2074", provision: "Section 116: Adjudication Tribunal", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "What is the role of the Cooperative Registrar in disputes?",
              "How are bad loans legally recovered from defaulting members?",
              "What is the penalty for board financial mismanagement?"
            ];
          }
        } 
        
        // 5. AUDIT / FINANCIAL Transparency
        else if (
          query.includes('audit') || 
          query.includes('financial') || 
          query.includes('ಲೆಕ್ಕ') || 
          query.includes('ಪರಿಶೋಧನೆ') || 
          query.includes('लेखा') || 
          query.includes('परीक्षण')
        ) {
          if (language === 'kn') {
            response.answer = "ಸಹಕಾರ ಸಂಘಗಳ ಲೆಕ್ಕಪರಿಶೋಧನೆ (Audit) ಮತ್ತು ಹಣಕಾಸಿನ ಪಾರದರ್ಶಕತೆಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ಈ ಕೆಳಗಿನ ನಿಯಮಗಳಿವೆ:";
            response.steps = [
              "ಆಂತರಿಕ ಲೆಕ್ಕಪರಿಶೋಧನೆ: ಮಹಾಸಭೆಯಿಂದ ಆಯ್ಕೆಯಾದ 3 ಸದಸ್ಯರ ಸಮಿತಿಯು ಪ್ರತಿ ತ್ರೈಮಾಸಿಕದ ಹಣಕಾಸು ವ್ಯವಹಾರವನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ.",
              "ವಾರ್ಷಿಕ ಲೆಕ್ಕಪರಿಶೋಧನೆ: ಆರ್ಥಿಕ ವರ್ಷ ಮುಗಿದ 6 ತಿಂಗಳೊಳಗೆ ನೋಂದಾಯಿತ ಆಡಿಟರ್ ಅವರಿಂದ ವಾರ್ಷಿಕ ಆಡಿಟ್ ಮಾಡಿಸುವುದು ಕಡ್ಡಾಯ.",
              "ಮಹಾಸಭೆಯಲ್ಲಿ ಮಂಡನೆ: ಆಡಿಟ್ ವರದಿಯನ್ನು ವಾರ್ಷಿಕ ಮಹಾಸಭೆಯ (AGM) ಮುಂದೆ ಮಂಡಿಸಿ ಅನುಮೋದನೆ ಪಡೆಯಬೇಕು."
            ];
            response.notes = ["ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಲೆಕ್ಕಪರಿಶೋಧನೆ ಸಲ್ಲಿಸದಿದ್ದರೆ ಸಂಘಕ್ಕೆ ದಂಡ ವಿಧಿಸಲಾಗುತ್ತದೆ ಮತ್ತು ನೋಂದಣಿ ರದ್ದಾಗಬಹುದು."];
            response.provisions = ["ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆಯ ಸೆಕ್ಷನ್ 73"];
            response.documents = ["ಆಸ್ತಿ ಜವಾಬ್ದಾರಿ ಪಟ್ಟಿ (Balance Sheet)", "ಲಾಭ ಮತ್ತು ನಷ್ಟದ ಪಟ್ಟಿ", "ಲೆಕ್ಕಪರಿಶೋಧಕರ ವರದಿ"];
            response.sources = [
              { documentName: "ಸಹಕಾರ ಸಂಘಗಳ ಕಾಯ್ದೆ", provision: "ಸೆಕ್ಷನ್ 73: ಲೆಕ್ಕಪರಿಶೋಧನೆ", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ಲೆಕ್ಕಪರಿಶೋಧಕರನ್ನು ಯಾರು ನೇಮಿಸುತ್ತಾರೆ?",
              "ಮಂಡಳಿ ಹಣ ದುರುಪಯೋಗ ಪಡಿಸಿಕೊಂಡರೆ ಎಲ್ಲಿ ದೂರು ನೀಡಬೇಕು?",
              "ಠೇವಣಿ ಸುರಕ್ಷತೆ ನಿಯಮಗಳೇನು?"
            ];
          } else if (language === 'ne') {
            response.answer = "सहकारीको लेखापरीक्षण (Audit) र वित्तीय पारदर्शिता सम्बन्धी कानूनी नियमहरू यस प्रकार छन्:";
            response.steps = [
              "आन्तरिक लेखापरीक्षण: साधारण सभाद्वारा निर्वाचित ३ सदस्यीय आन्तरिक लेखा सुपरिवेक्षण समितिले त्रैमासिक रूपमा वित्तीय अनुगमन गर्दछ।",
              "बाह्य लेखापरीक्षण: आर्थिक वर्ष समाप्त भएको ६ महिनाभित्र रजिष्ट्रार कार्यालयबाट स्वीकृत प्राप्त दर्तावाल लेखापरीक्षक (Auditor) बाट विस्तृत बाह्य लेखापरीक्षण गराउनु अनिवार्य छ।",
              "साधारण सभामा प्रस्तुती: लेखापरीक्षण प्रतिवेदन साधारण सभा (AGM) मा प्रस्तुत गरी छलफल र अनुमोदन गराउनुपर्दछ।"
            ];
            response.notes = ["लेखापरीक्षण नगराउने वा ढिलो गराउने सहकारीलाई कानून बमोजिम नगद जरिवाना हुने व्यवस्था छ।"];
            response.provisions = ["सहकारी ऐन, २०७४ को दफा ७३ (लेखापरीक्षण)"];
            response.documents = ["वासलात (Balance Sheet)", "नाफा नोक्सान हिसाब (Profit & Loss)", "नगद प्रवाह विवरण (Cash Flow)"];
            response.sources = [
              { documentName: "सहकारी ऐन, २०७४", provision: "दफा ७३: लेखापरीक्षण सम्बन्धी व्यवस्था", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "लेखापरीक्षक कसले नियुक्त गर्छ?",
              "लेखापरीक्षण नगरेमा के जरिवाना हुन्छ?",
              "तरलता अनुपात (Liquidity Ratio) कति हुनुपर्छ?"
            ];
          } else if (language === 'hi') {
            response.answer = "सहकारी समिति के ऑडिट (लेखापरीक्षा) और वित्तीय नियमों के संदर्भ में निम्नलिखित बातें अनिवार्य हैं:";
            response.steps = [
              "आंतरिक ऑडिट: सदस्यों द्वारा निर्वाचित 3 सदस्यीय ऑडिट समिति हर तिमाही वित्तीय लेनदेन की जांच करती है।",
              "वैधानिक ऑडिट: वित्तीय वर्ष समाप्त होने के 6 महीने के भीतर रजिस्ट्रार द्वारा अनुमोदित चार्टर्ड अकाउंटेंट (CA) से ऑडिट कराना अनिवार्य है।",
              "साधारण सभा में अनुमोदन: ऑडिट रिपोर्ट को वार्षिक साधारण सभा (AGM) में रखा जाना चाहिए और इसे पारित किया जाना चाहिए।"
            ];
            response.notes = ["यदि ऑडिट समय पर नहीं होता है, तो समिति के सदस्यों पर जुर्माना लगाया जा सकता है और पंजीकरण रद्द भी हो सकता है।"];
            response.provisions = ["सहकारी अधिनियम, 2074 की धारा 73 (लेखापरीक्षा)"];
            response.documents = ["तुलन पत्र (Balance Sheet)", "आय-व्यय विवरण", "ऑडिटर की रिपोर्ट"];
            response.sources = [
              { documentName: "सहकारी अधिनियम, 2074", provision: "धारा 73: ऑडिट नियम", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "ऑडिटर की नियुक्ति कौन करता है?",
              "सहकारी के लिए अनिवार्य रिजर्व फंड क्या हैं?",
              "ब्याज दर पर क्या सीमाएं हैं?"
            ];
          } else {
            response.answer = "Cooperatives must adhere to strict financial transparency guidelines, consisting of internal and statutory external audits:";
            response.steps = [
              "Internal Audit: Executed by an elected 3-member Supervisory Audit Committee to perform continuous quarterly cash and transaction checks.",
              "Statutory External Audit: Must be conducted annually by a certified Registered Auditor nominated from the Registrar's approved list, completed within 3 months of fiscal year-end.",
              "Submission & Presentation: Submit the final audit report to the Registrar and present it for approval in the General Assembly within 6 months of fiscal year-end."
            ];
            response.notes = ["Crucial: Failure to submit audit reports within 6 months triggers financial fines and can lead to blacklisting or license cancellation."];
            response.provisions = ["Section 73 (Auditing) of the Cooperative Act, 2074"];
            response.documents = ["Annual Balance Sheet", "Income and Expenditure Statement", "Cash Flow Statement", "Auditor's Compliance Note"];
            response.sources = [
              { documentName: "Cooperative Act, 2074", provision: "Section 73: Audit Requirements", id: "cooperative-act-2074" }
            ];
            response.suggestedQuestions = [
              "Who appoints the external auditor?",
              "What are the penalties for late audit submissions?",
              "What is the Cash Reserve Ratio (CRR) required for financial cooperatives?"
            ];
          }
        } 
        
        // 6. GENERAL FALLBACK RESPONSE
        else {
          if (language === 'kn') {
            response.answer = `ನಿಮ್ಮ ಪ್ರಶ್ನೆ "${messageText}" ಅನ್ನು ನಾನು ಸ್ವೀಕರಿಸಿದ್ದೇನೆ. ಸಹಕಾರಿ ಕಾಯ್ದೆಯಡಿ ಇದು ಮುಖ್ಯವಾದ ವಿಷಯವಾಗಿದೆ.`;
            response.steps = [
              "ಸಹಕಾರ ಸಂಘಗಳು ಮೂಲತಃ ಸದಸ್ಯರ ಪರಸ್ಪರ ಆರ್ಥಿಕ ಮತ್ತು ಸಾಮಾಜಿಕ ಹಿತಾಸಕ್ತಿಗಳಿಗಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತವೆ.",
              "ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ನೀವು ನಮ್ಮ 'ಸಹಕಾರ ಮಾರ್ಗದರ್ಶಿ' ಅಥವಾ 'ಕಾನೂನು ಸಂಪನ್ಮೂಲಗಳು' ಪುಟಗಳನ್ನು ನೋಡಬಹುದು.",
              "ಸಹಕಾರ ಸಂಘದ ನೋಂದಣಿ, ಸದಸ್ಯತ್ವದ ನಿಯಮಗಳು ಮತ್ತು ಆಡಳಿತ ಮಂಡಳಿಯ ಬಗ್ಗೆ ನೀವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು."
            ];
            response.suggestedQuestions = [
              "ಸಹಕಾರ ಸಂಘ ನೋಂದಾಯಿಸುವುದು ಹೇಗೆ?",
              "ಸದಸ್ಯರ ಹಕ್ಕುಗಳು ಏನೇನು?",
              "ಆಡಳಿತ ಮಂಡಳಿಯ ರಚನೆ ಹೇಗೆ?"
            ];
          } else if (language === 'ne') {
            response.answer = `मैले तपाईंको प्रश्न: "${messageText}" बुझें। सहकारी ऐन र शासनका सन्दर्भमा यो एउटा महत्त्वपूर्ण विषय हो।`;
            response.steps = [
              "सहकारी संस्था मुख्यतया आफ्ना सदस्यहरूको आपसी हित र सहकार्यका लागि स्थापना हुन्छन्।",
              "यस सम्बन्धमा विस्तृत जानकारीका लागि हाम्रो 'सहकारी निर्देशिका' वा 'कानूनी स्रोतहरू' पृष्ठहरू हेर्न सक्नुहुन्छ।",
              "यदि तपाईं सहकारी दर्ता, सदस्य अधिकार, वा विवाद समाधान सम्बन्धी कुरा बुझ्न चाहनुहुन्छ भने सोही अनुसारका प्रश्न सोध्न सक्नुहुन्छ।"
            ];
            response.provisions = ["नेपाल सहकारी ऐन तथा नियमावलीका साधारण सिद्धान्तहरू"];
            response.suggestedQuestions = [
              "सहकारी दर्ता कसरी गर्ने?",
              "सदस्यका अधिकारहरू के-के हुन्?",
              "विवाद परेमा कहाँ उजुरी गर्ने?"
            ];
          } else if (language === 'hi') {
            response.answer = `मैंने आपका प्रश्न: "${messageText}" समझा। सहकारी नियमों के अंतर्गत यह एक महत्वपूर्ण विषय है।`;
            response.steps = [
              "सहकारी समितियां पूरी तरह से लोकतांत्रिक सिद्धांतों और सामाजिक विकास पर आधारित होती हैं।",
              "इस विषय में अधिक विशिष्ट जानकारी के लिए कृपया 'सहकारी गाइड' या 'कानूनी संसाधन' देखें।",
              "आप मुझसे विशेष रूप से पंजीकरण, समिति गठन, सदस्यों के अधिकार, ऑडिट, या विवादों के निपटारे के बारे में पूछ सकते हैं।"
            ];
            response.suggestedQuestions = [
              "सहकारी पंजीकरण कैसे करें?",
              "सहकारी सदस्य के अधिकार क्या हैं?",
              "विवादों का समाधान कैसे होता है?"
            ];
          } else {
            response.answer = `I understand your question regarding "${messageText}". While I retrieve information for this specific query, here are the general cooperative guidelines:`;
            response.steps = [
              "Cooperatives are self-help organizations based on community development and mutual business operations.",
              "For detailed legal sections, please browse the 'Legal Resources' tab or check our curated 'Cooperative Guide' sections.",
              "You can ask me specific questions about cooperative registration, board management, audit guidelines, or conflict resolution."
            ];
            response.suggestedQuestions = [
              "How to register a cooperative?",
              "What are member rights and voting rules?",
              "How to resolve a cooperative dispute?"
            ];
          }
        }

        resolve(response);
      }, 1200);
    });
  }
};
export default chatService;
