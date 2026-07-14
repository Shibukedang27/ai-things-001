import type { CodeAnalysisResult, CodeRunResult, CodeSubmission, CodeTemplate } from "./types";

export const codeTemplates: Record<CodeTemplate["language"], CodeTemplate> = {
  python: {
    language: "python",
    label: "Python",
    promptTitle: "Two Sum Optimization",
    prompt: "Return indices of two numbers that add up to the target. Optimize beyond the brute-force nested loop.",
    sourceCode:
      "def two_sum(nums, target):\n" +
      "    for i in range(len(nums)):\n" +
      "        for j in range(i + 1, len(nums)):\n" +
      "            if nums[i] + nums[j] == target:\n" +
      "                return [i, j]\n" +
      "    return []\n\n" +
      "print(two_sum([2, 7, 11, 15], 9))\n",
    stdin: "",
    expectedOutput: "[0, 1]",
  },
  java: {
    language: "java",
    label: "Java",
    promptTitle: "Array Pair Search",
    prompt: "Find two array positions whose values add to the target. Use a scalable data structure.",
    sourceCode:
      "import java.util.*;\n\n" +
      "class Main {\n" +
      "    static int[] twoSum(int[] nums, int target) {\n" +
      "        for (int i = 0; i < nums.length; i++) {\n" +
      "            for (int j = i + 1; j < nums.length; j++) {\n" +
      "                if (nums[i] + nums[j] == target) {\n" +
      "                    return new int[] { i, j };\n" +
      "                }\n" +
      "            }\n" +
      "        }\n" +
      "        return new int[0];\n" +
      "    }\n\n" +
      "    public static void main(String[] args) {\n" +
      "        System.out.println(Arrays.toString(twoSum(new int[] {2, 7, 11, 15}, 9)));\n" +
      "    }\n" +
      "}\n",
    stdin: "",
    expectedOutput: "[0, 1]",
  },
  sql: {
    language: "sql",
    label: "SQL",
    promptTitle: "Top Candidate Scores",
    prompt: "Return each candidate with their highest interview score, ordered by score descending.",
    sourceCode:
      "CREATE TABLE interview_scores (\n" +
      "    candidate TEXT,\n" +
      "    score INTEGER\n" +
      ");\n\n" +
      "INSERT INTO interview_scores (candidate, score) VALUES\n" +
      "('Avery', 91),\n" +
      "('Maya', 96),\n" +
      "('Avery', 88);\n\n" +
      "SELECT candidate, MAX(score) AS highest_score\n" +
      "FROM interview_scores\n" +
      "GROUP BY candidate\n" +
      "ORDER BY highest_score DESC;\n",
    stdin: "",
    expectedOutput: "",
  },
};

export const initialRunResult: CodeRunResult = {
  language: "python",
  status: "skipped",
  stdout: "Run code to see execution output.",
  stderr: "",
  exit_code: null,
  execution_time_ms: null,
  memory_kb: null,
  passed: null,
};

export const initialAnalysis: CodeAnalysisResult = {
  language: "python",
  time_complexity: "Pending",
  space_complexity: "Pending",
  bugs: [],
  optimized_code: "Analyze code to generate an optimized version.",
  improvement_explanation: "Complexity, bug detection, and improvement guidance will appear here after analysis.",
  improvement_suggestions: ["Run analysis when your solution is ready."],
  quality_score: "0.00",
  observations: ["Editor initialized with a Python challenge."],
  analyzer_version: "pending",
};

export const sampleSubmissions: CodeSubmission[] = [
  {
    id: "SUB-2042",
    language: "python",
    prompt_title: "Two Sum Optimization",
    status: "success",
    time_complexity: "O(n)",
    space_complexity: "O(n)",
    execution_time_ms: 18,
    submitted_at: "Today",
  },
  {
    id: "SUB-2038",
    language: "sql",
    prompt_title: "Top Candidate Scores",
    status: "success",
    time_complexity: "O(n log n)",
    space_complexity: "O(n)",
    execution_time_ms: 9,
    submitted_at: "Yesterday",
  },
  {
    id: "SUB-2032",
    language: "java",
    prompt_title: "Array Pair Search",
    status: "failed",
    time_complexity: "O(n^2)",
    space_complexity: "O(1)",
    execution_time_ms: 42,
    submitted_at: "Jul 12",
  },
];
