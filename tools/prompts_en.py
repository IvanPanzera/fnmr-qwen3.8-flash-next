"""English reading translations of the original synthetic task templates.
Literal code and data keys are retained so the task remains inspectable.
These texts were NOT used to collect routing traces.
"""
TASKS={
'codice':'''Deduplication|Write a Python function that deduplicates records by id, keeping the last record and the order of first occurrence.
Intervals|Write a JavaScript function that merges overlapping time intervals and calculates their total duration.
CSV parsing|Write Python code using csv to read a semicolon-delimited CSV with comma decimal separators in amounts.
LRU cache|Implement a small Python LRU cache with get, put and capacity {a}; use OrderedDict.
Validator|Write a TypeScript function that validates an order object, distinguishing missing fields from incorrect types.
Search|Write a binary search in C that returns the first index of a duplicated value, or -1.
Graph|Write a Python BFS function that returns the shortest unweighted path between two nodes, or None.
Large files|Write a Python generator that reads a text file in chunks and yields complete lines, including lines split across chunks.
Dates|Write a JavaScript function that groups events by UTC day without depending on the local time zone.
Retry|Write an asynchronous Python function with at most {a} attempts, exponential backoff and propagated cancellation.
Aggregation|Write a Rust function that calculates counts and sums by category from a sequence of pairs.
CLI arguments|Write a short Python argparse program with an input path, output format and dry-run option.
JSON stream|Write Python code that filters JSONL records without loading the entire file into memory.
Producer–consumer|Write a Python example using queue and two threads that shut down cleanly with a sentinel.
UI components|Write a React TypeScript component for a filterable list with a count and an empty state.
Paginated API|Write a Python function that traverses API pages using next_cursor and detects repeated cursors.
Normalization|Write a Go function that normalizes whitespace and lowercase in strings while preserving Unicode characters.
Parameterized tests|Write a Python median function and parameterized pytest tests, including empty input and even length.
Sorting|Write a C++ function that sorts records first by descending priority and then by ascending name.
Safe shell|Write a PowerShell script that lists the largest files in a folder without modifying them.''',
'debug':'''List mutation|Fix: def positive(xs):\n for x in xs:\n  if x < 0: xs.remove(x)\n return xs
Mutable default|Fix: def add(x, items=[]):\n items.append(x)\n return items
Integer division|Fix the C mean calculation: double mean(int total,int count) {{ return total/count; }}. Handle count=0.
Closure|Fix JavaScript: const f=[]; for(var i=0;i<3;i++) f.push(()=>i); console.log(f.map(x=>x()));
SQL null|Fix SQL: SELECT * FROM orders WHERE shipped_at = NULL;
Join|Fix a customer–order LEFT JOIN whose WHERE orders.status='paid' excludes customers without orders.
UTC dates|Identify the problem with grouping UTC events using new Date(ts).getDate() and propose a verifiable fix.
Off-by-one|Fix Python: for i in range(len(xs)+1): print(xs[i]). Explain the empty-list case.
Async|Fix: async def fetch_all(urls): return [fetch(u) for u in urls]. fetch is asynchronous.
Race condition|Two threads execute if key not in cache: cache[key]=expensive(). Explain the race and prevent duplicate work.
File resource|Fix a function that opens a file, may raise exceptions, and closes it only immediately before return.
Matrix aliases|Fix Python: grid=[[0]*{a}]*{b}; grid[0][0]=1. The other rows must not change.
Floating-point sum|A test expects 0.1+0.2==0.3. Fix the test without indiscriminately rounding all data.
Pagination|A pagination loop reuses the initial cursor in every request. Identify the fault and propose tests.
Regex|An email regex accepts spaces and newlines. Propose a pragmatic check and state its limits.
Exceptions|Fix Python: try: return int(s) except Exception: return 0. Invalid input must be distinguished from a valid zero.
Overflow|A sum of amounts in cents uses int32 and exceeds its limit. Suggest a fix and boundary tests.
Test order|A test passes alone but fails after another test changes a global variable. Diagnose and isolate the state.
React effect|A useEffect without dependencies updates state on every render. Show the loop and a minimal fix.
Encoding|A UTF-8 CSV with a BOM produces an unexpected first-column name. Diagnose and fix the reader.''',
'dati':'''SQL totals|Write PostgreSQL SQL for total amounts and record counts by department, including only status approvato (approved).
Top per group|Write PostgreSQL SQL for the record with the largest amount in each department, breaking ties by id.
Time series|Calculate the mean and percentage change of the series values; flag zero denominators.
Median|Calculate the median and quartiles, stating the convention used.
Customer join|Design a customer–order LEFT JOIN that retains all customers and returns zero for missing aggregates.
Duplicates|Identify duplicates by reparto and importo (department and amount), without confusing different ids with identical records.
Missing values|Propose missing-data handling that distinguishes absence, zero and an invalid value.
SQL window|Write SQL for a cumulative sum of amounts ordered by date, separately for each department.
Group comparison|Compare departments' mean amounts; describe what cannot be inferred causally.
Pivot|Describe a department-by-status pivot table with counts and totals, and provide pandas code.
Cleaning|Write pandas code to convert textual amounts with decimal commas and flag failed conversions.
Outliers|Assess the series' outliers using a robust rule, showing the threshold and identified cases.
Percentages|Calculate each department's share of the total without averaging percentages with different denominators.
SQL indexes|For status/date filters and department aggregation, propose PostgreSQL indexes and a way to verify them.
Schema|Design a normalized relational schema for departments, cases and status changes.
Incremental ETL|Propose an idempotent incremental ETL using an update date and a primary key.
Histogram|Propose bins for a histogram of the amounts and explain how to avoid a misleading representation.
Data quality|Define five automatic quality checks for the register, with examples of anomalies.
Sampling|Propose stratified sampling by department and explain how to estimate the total.
SQL deduplication|Write a SELECT that chooses the most recent version per id using row_number and deterministic ordering.''',
'matematica':'''Equation|Solve {a}x+{b}={c}, checking by substitution.
System|Solve x+y={a}, 2x-y={b} and verify both equations.
Percentages|A price of {c} euros increases by {a}% and then decreases by {b}%. Calculate the final price and overall change.
Probability|An urn contains {a} red balls and {b} blue balls. Calculate the probability of drawing two red balls without replacement.
Derivative|Differentiate f(x)={a}x^3-{b}x^2+{c} and find its stationary points.
Integral|Calculate the integral of {a}x^2+{b} from 0 to 2, showing the steps.
Vectors|Calculate the dot product and angle between ({a},1,0) and (0,{b},1).
Matrix|Calculate the determinant and inverse, if it exists, of [[{a},1],[2,{b}]].
Interest|Principal {c} euros, annual rate {a}% for 3 years: compare simple and compound interest.
Combinatorics|Choose 2 of {a} distinct elements without order or repetition. Calculate the number of combinations.
Progression|An arithmetic progression starts at {a}, has common difference {b}, and 12 terms. Calculate its last term and sum.
Geometry|A cylinder has radius {a} cm and height {b} cm. Calculate its exact volume and total surface area.
Logarithms|Solve log2(x-{a})=3, stating the domain and checking the solution.
Limit|Calculate the limit as x approaches 0 of sin({a}x)/x and explain the argument.
Bayes|2% of parts are defective. A test has 90% sensitivity and 5% false positives. Calculate P(defect|positive).
Optimization|A rectangle has perimeter {c} cm. Find the dimensions with maximum area and justify them.
Conversion|Convert {a} m/s to km/h and {c} cm^3 to liters, explicitly giving the conversion factors.
Numerical method|Apply two Newton iterations to x^2-{a}=0 starting at x0=2; mention possible limitations.
Errors|A measurement is {c} ± {a} mm. Calculate the relative error and first-order propagation to a square's area.
Series|Calculate the sum of the first 8 terms of the geometric progression with first term {a} and ratio 2.''',
'logica':'''Syllogism|All A modules are tested. Some tested modules are defective. Does it follow that some A modules are defective? Give a counterexample if not.
Ordering|Anna precedes Bruno; Carla follows Anna but precedes Diego; Bruno follows Diego. Find the order and verify the constraints.
Conditional|If a file is encrypted, a key is needed. I have a key. Can I conclude that the file is encrypted? Explain.
Scheduling|Three jobs take {a}, {b}, {c} minutes. The third depends on the first two, which can run in parallel. Calculate the minimum time.
Sets|In a group of 100 people, 60 know A, 50 know B and 30 know both. How many know neither and how many know exactly one language?
Invariant|A process adds or subtracts 2 from an initially even number. Can it reach {odd}? Prove the answer.
Truth|A says B is lying. B says they are both lying. Assuming each is always truthful or always a liar, find a configuration or prove inconsistency.
Constraints|Four activities P,Q,R,S: P before R, Q before R, R before S. List every valid order.
Diagnosis|Three possible causes explain a failure; each is consistent with a common symptom. Why does the symptom alone not identify the cause?
Counterexample|Is the statement all prime numbers are odd true? Correct it with the smallest necessary exception.
Decision|Two alternatives cost {c} and {d}; the first requires {a} hours and the second {b}. Describe the Pareto frontier without inventing preferences.
Necessary and sufficient|Having a valid password is necessary but not sufficient for access. List compatible and incompatible cases.
Precedence|A job requires design, review, approval and purchasing; review follows design, purchasing follows approval. Can approval precede review? State when a constraint is missing.
Quantifiers|Distinguish for every project there is a person in charge from there is one person in charge of all projects. Give a concrete example.
False dilemma|A text says: either we automate everything immediately or we will remain inefficient. Analyze the argument and propose logical alternatives.
Pigeonhole principle|We distribute 13 objects among 12 boxes. Prove that one box contains at least 2 without assuming a uniform distribution.
Recursion|Define a recursive rule for the sum from 1 to n and prove n(n+1)/2 by induction.
Calendar|Event A occurs every 6 days, B every 8; they coincide today. When do they coincide again? Show the reasoning.
Ambiguity|The statement everyone has read at least one document does not mean everyone has read the same document. Explain with a minimal table.
Consistency|The requirements demand exactly {a} modules and at least {c} modules, with c greater than a. Identify the conflict and the smallest change.''',
'ingegneria':'''Beam|For a simply supported beam with span {a} m and uniform load {b} kN/m, calculate reactions and maximum bending moment, stating the idealized model.
DC circuit|Resistors of {a} and {b} ohms in series are supplied at 24 V. Calculate current, voltages and total power.
Pump|Flow {a} L/s, head {b} m, efficiency 70%. Estimate electrical power for water and check units.
Heat transmission|Wall area 10 m², U=1.2 W/(m² K), temperature difference {a} K. Estimate heat loss in the steady-state model.
Tolerances|Two nominal dimensions {a} and {b} mm have tolerances of ±0.1 mm. Determine the worst-case tolerance of their sum.
FMEA|Prepare a short FMEA for a valve that can stick open or closed; do not assign arbitrary scores without criteria.
Sensors|Design a sensor calibration procedure using five points, repeatability and a hysteresis check.
PID|Explain how to recognize integral windup in a PID and how anti-windup works.
Energy balance|A {a} kW heater operates {b} hours per day. Calculate energy over 30 days and cost at 0.25 euros/kWh.
Pipe flow|A pipe has internal diameter 50 mm and flow velocity {a} m/s. Calculate flow rate and specify that you are not sizing pressure losses.
Signals|A signal contains frequencies up to {c} Hz. Explain the theoretical minimum sampling frequency and a practical margin.
RC network|R={a} kohm and C={b} microfarads. Calculate the time constant and step response at t=tau.
Reliability|Two independent components have reliabilities 0.98 and 0.95: compare ideal series and parallel configurations.
Bill of materials|Propose a bill of materials for a small control panel, distinguishing required data and assumptions.
Dimensional analysis|Check the dimensions of F=ma, E=Pt and a proposed formula Q=v/D; correct the last for a circular cross-section.
Acceptance testing|Propose a functional test plan for a device with an analog input and two digital outputs.
Project risks|Prepare a short risk register for installing a sensor in a humid environment, with verifiable mitigations.
Maintenance|Compare preventive and condition-based maintenance for a pump, indicating the data needed to choose.
Requirements|Turn the vague requirement the system must be fast into three verifiable requirements, without pretending that the thresholds have already been approved.
Heat transfer|Estimate the heat needed to warm {a} kg of water from 20 to 60 °C, assuming c=4.18 kJ/(kg K).''',
'scienze':'''Light scattering|Explain Rayleigh scattering and why the sky looks different at sunset.
Osmosis|Explain osmosis, distinguishing it from diffusion, with an example and a limit of the analogy.
Entropy|Explain the second law and why a refrigerator does not violate it.
Photosynthesis|Describe the inputs, products and role of light in photosynthesis without confusing respiration with photosynthesis.
Evolution|Explain natural selection and genetic drift with an example that distinguishes them.
Bonds|Compare ionic, covalent and metallic bonding, avoiding overly absolute categories.
Acids and bases|Explain pH and the difference between a strong acid and a concentrated solution.
Waves|Compare speed, frequency and wavelength; use a numerical example with frequency {c} Hz.
Gravity|Explain why astronauts in orbit are in free fall even though gravity is not zero.
Climate|Distinguish weather from climate and explain why one day is insufficient to assess a trend.
Statistics in science|Explain correlation and causation and propose an experiment with a control.
DNA|Explain the DNA–RNA–protein flow, including a caution about the simplification.
Vaccine concept|Describe immune memory and the secondary response in general terms, without clinical advice.
Geology|Compare igneous, sedimentary and metamorphic rocks and their cycle.
Radioactivity|Explain half-life and calculate the remaining fraction after three half-lives.
Conservation|Explain conservation of mass in a reaction in a closed system and the role of gases.
Electromagnetism|Explain electromagnetic induction and why change in flux matters.
Scientific method|Turn a question about plant growth into a falsifiable hypothesis and a controlled experiment.
Pressure|Explain why hydrostatic pressure depends on depth and density, with an example at {a} meters.
Equilibrium|Explain chemical dynamic equilibrium without describing it as reactions stopping.''',
'documenti':'''Executive summary|Summarize the document in five points, separating facts, decisions and open questions.
Minutes|Turn the notes into concise minutes with decisions and actions, without adding absent assignments.
Comparison|Compare the departments based on the document and identify differences and missing information.
Chronology|Reconstruct events in chronological order with references to source lines.
Risks|Extract issues and dependencies from the document, distinguishing explicit risks from possible inferences.
Short summary|Summarize in at most 80 words without losing essential deadlines and amounts.
FAQ|Create four questions and answers based solely on the document.
Actions|Organize actions by person responsible, identifying missing deadlines without inventing them.
Ambiguity|Identify ambiguous wording and write clarification questions for the author.
Inconsistencies|Look for internal contradictions and differences between proposed and confirmed budgets.
Table|Reorganize the document into a compact table while retaining traceability to its lines.
Abstract|Produce a neutral abstract suitable for a technical archive.
Handover|Prepare a handover highlighting completed activities and those still pending.
Evidence only|List five claims supported by the document and identify the source line for each.
Plain language|Rewrite the main content for a nonspecialist reader without adding conclusions.
Headings|Propose a structure of sections and subsections that makes the text easy to consult.
Decision log|Build a decision log distinguishing proposals from actual approvals.
Comparative summary|Summarize differences between the initial state and later updates described in the document.
Limits|State which questions cannot be answered from the document and what data would be needed.
Priorities|Propose justified priorities using only explicit deadlines and constraints, and flag ties.''',
'estrazione':'''JSON filter|Return only a JSON array of approved cases (stato=approvato) in department impianti, with id and numeric importo.
ISO dates|Extract ids and dates, converting dates to ISO 8601; use null for missing dates. JSON only.
Entities|Extract people and departments without duplicates, preserving the order of first occurrence. JSON only.
Strict schema|Produce JSON with keys records and count, with no additional keys; include only suspended cases (stato=sospeso).
Sums|Return JSON with the sum of amounts by department, excluding records with a missing amount.
CSV|Convert the data to CSV with columns id,reparto,stato,importo; use quotes where necessary.
JSON actions|Extract actions and people responsible into JSON, leaving null where information is not explicit.
Validation|Flag in JSON records without an id, with negative amounts or with unrecognized statuses; do not silently correct them.
Amount threshold|Extract into JSON records whose amount exceeds {c}, ordered by descending amount.
Grouping|Return a JSON object mapping each status to an array of ids.
Null fields|Normalize missing amounts to null and empty responsabile strings to null, without inventing values.
NDJSON|Convert each record into an independent JSON line, retaining the original fields.
Counts|Return only JSON with case counts by status and the overall count.
Field selection|Extract only id and responsabile from records in department strutture. Include no other fields. JSON only.
Maximum|Return JSON for the record with the largest amount and all ties, ignoring missing amounts.
Minimum|Return JSON for the approved record with the smallest amount and all ties.
Deduplication|Return unique ids in JSON in their original order and the repetition count per id.
Checklist|Produce JSON with booleans for the presence of a date, responsible person and amount in each record.
Intersection|Extract ids of approved cases with an amount above {c} and a date present. JSON only.
English keys|Transform the records into JSON with keys id,department,status,amount,owner,date; do not translate proper names.''',
'traduzione':'''IT → EN|Translate the Italian text into natural English, preserving numbers and proper names.
IT → FR|Translate the Italian text into French, maintaining a professional register.
IT → DE|Translate the Italian text into German, retaining units and deadlines.
IT → ES|Translate the Italian text into Spanish without summarizing it.
EN → IT|Translate the English text into natural Italian, avoiding unnecessary calques.
Technical|Translate the Italian technical text into English and add three justified terminology choices.
Formal|Translate the text into formal English suitable for communication between companies.
Conversational|Translate the text into conversational English without altering the facts.
Parallel|Produce a table with each Italian sentence and its English counterpart.
Localization|Localize the text into British English, preserving amounts in euros and unambiguous dates.
Glossary|Create an Italian–English glossary of five terms in the text with their contextual meanings.
English editing|Improve the English text for clarity and grammar and identify two main corrections.
Simple|Translate into B1 English with short sentences without losing operational information.
Ambiguity|Translate into English and flag any ambiguity in the original rather than resolving it arbitrarily.
Headings|Translate into English and propose an informative title consistent with the content.
Syntax|Explain two syntactic differences between the Italian text and your English translation.
Consistent terminology|Translate into French, always using the same term for the same technical concept.
Subtitles|Translate into English in short lines suitable for subtitles, without omitting information.
Pronouns|Translate into Spanish, paying attention to pronoun references and explicit responsibilities.
Polite tone|Translate into English in a polite but firm tone, without introducing threats or commitments.''',
'professionale':'''Follow-up email|Write a polite email asking for an update on a late delivery.
Agenda|Prepare a meeting agenda with objectives and expected decisions.
Project status|Write a project update distinguishing facts, risks and next actions.
Proposal|Write an intervention proposal with its objective, scope and data still to be confirmed.
Polite refusal|Write a justified refusal of an out-of-scope request, proposing a realistic alternative.
Handover|Prepare a clear and concise handover message.
Clarification request|Write a request for clarification of ambiguous requirements, with numbered questions.
Decision|Draft a note justifying a decision, distinguishing criteria and assumptions.
Delay notice|Communicate a delay, accepting responsibility without inventing a guaranteed new date.
Presentation|Prepare the opening of a technical presentation for nonspecialist executives.
Checklist|Write an operational checklist for checking a document delivery.
Action minutes|Draft short minutes with the supplied actions, people responsible and deadlines.
Proposal summary|Summarize a proposal in 100 words, focusing on the recipient's benefit.
Feedback|Give constructive feedback on an incomplete document, with verifiable actions.
Instructions|Write numbered operating instructions for a colleague taking over the project.
Escalation|Prepare an escalation note describing the impact and decision needed without an accusatory tone.
Email subject|Propose three email subjects and write the most appropriate message.
Negotiation|Write a response proposing a scope reduction to stay within budget.
Weekly report|Prepare a short weekly report with progress, impediments and next steps.
Invitation|Write an invitation to a project review specifying the preparation and expected outcome.''',
'creativa':'''Story|Write a micro-story with a conflict and a nontrivial ending.
Dialogue|Write a dialogue between two characters with opposing goals, allowing the conflict to emerge through their lines.
Opening|Write the opening of a story without immediately explaining the mystery.
Poem|Write a short free-verse poem using concrete imagery.
Description|Describe a place through sounds, smells and details without listing adjectives.
Science fiction|Write a science-fiction scene where an everyday technology has an unexpected consequence.
Mystery|Write an investigative scene with a visible clue that can be interpreted in two ways.
Fairy tale|Write a short fairy tale with a difficult choice and an implicit moral.
Comedy|Write a comic scene based on a misunderstanding that is resolved at the end.
Monologue|Write a monologue that reveals a hidden desire without naming it directly.
First person|Tell a discovery in the first person with a narrator who is not entirely reliable.
Second person|Write a short second-person scene with a concrete choice of paths.
Letter|Write an imaginary letter that hints at an earlier story.
Alternative ending|Write two short endings, one open and one conclusive, for the proposed situation.
Lexical constraint|Write a scene without using the words bello, strano and improvvisamente (beautiful, strange and suddenly).
Setting|Describe a familiar place as if seen for the first time by an inexperienced visitor.
Film premise|Propose a film premise with a protagonist, an obstacle and something at stake.
Flashback|Write a scene containing a short flashback clearly distinguishable from the present.
Change of tone|Tell the same situation first in a comic tone and then in a melancholy tone, in two short paragraphs.
Narrating object|Have an inanimate object narrate the situation, maintaining a consistent point of view.'''
}
AUDIENCES=['high-school student','technical colleague','nonspecialist reader','university student','project manager']
PLACES=['mountain library','coastal station','night laboratory','covered market','astronomical observatory','municipal archive','small theater','river port','abandoned greenhouse','bicycle workshop','empty museum','snowy mountain refuge','city apartment building','ferry underway','music school']
GLOSSARY='Data glossary: reparto = department; stato = status; importo = amount; responsabile = person responsible; data = date; impianti = building services; strutture = structures; edilizia = construction; approvato = approved; sospeso = suspended; in revisione = under review. Literal data below are retained verbatim.'
