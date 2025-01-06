<template>
    <div>
      <h1>Rittenhouse Framework Analysis</h1>
      <button @click="fetchAnalysisReports" :disabled="localIsProcessing">
        Make Rittenhouse Analysis
      </button>
      <!-- Loading Throbber -->
      <div v-if="localIsProcessing" class="loading-overlay">
        <div class="loading-throbber">
          <div class="spinner"></div>
          <p>Creating Rittenhouse analysis...</p>
        </div>
      </div>
      <!-- Legend for Sentiment Polarity and Subjectivity -->
      <div>
        <p><strong>Sentiment Polarity:</strong> Indicates the overall sentiment of the text, ranging from -1 (very negative) to 1 (very positive).</p>
        <p><strong>Sentiment Subjectivity:</strong> Measures how subjective or opinion-based the text is, ranging from 0 (very objective) to 1 (very subjective).</p>
      </div>
      <div v-if="analysisReports.length && !localIsProcessing">
        <!-- Loop through each file type to create a collapsible section -->
        <div v-for="(fileType, fileTypeIndex) in getFileTypes()" :key="fileTypeIndex">
          <!-- Expander Button -->
          <button class="expander" @click="toggleCollapse(fileType)">
            {{ fileType }} Rittenhouse Analysis Table
          </button>
          <!-- Collapsible Table -->
          <div v-if="!collapsed[fileType]">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Keyword</th>
                  <th v-for="reportData in analysisReports" :key="reportData.ticker">
                    Company: {{ reportData.ticker }}
                    <br>
                    File Name: {{ formatFileName(reportData.reports[fileTypeIndex].File) }}
                    <br>
                    <small>Polarity: {{ reportData.reports[fileTypeIndex]['Sentiment Polarity'].toFixed(2) }}</small>
                    <br>
                    <small>Subjectivity: {{ reportData.reports[fileTypeIndex]['Sentiment Subjectivity'].toFixed(2) }}</small>
                  </th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(category, catIndex) in getCategoriesForFileType(fileType)" :key="catIndex">
                  <tr v-for="(keywordData, keyIndex) in getSortedKeywordsForFileType(fileType, category)" :key="keyIndex">
                    <!-- Display the category name only for the first keyword in each category -->
                    <td v-if="keyIndex === 0" :rowspan="getKeywordsForFileType(fileType, category).length">
                    <h2>{{ category }}</h2>
                    </td>
                    <td>{{ keywordData.keyword }}</td>
                    <!-- Loop through each ticker to get the value -->
                    <td v-for="reportData in analysisReports" :key="reportData.ticker">
                      {{ keywordData.counts[reportData.ticker] || 0 }}
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref } from 'vue';
  
  export default {
    props: {
      tickers: {
        type: Array,
        required: true,
      },
      // companies: {
      //   type: Object,
      //   required: true,
      // },
      isProcessing: Boolean,
    },
    setup(props, { emit }) {
      const analysisReports = ref([]);
      const collapsed = ref({});
      const localIsProcessing = ref(props.isProcessing);
  
      const toggleCollapse = (fileType) => {
        collapsed.value[fileType] = !collapsed.value[fileType];
      };
  
      const fetchAnalysisReports = async () => {
        if (localIsProcessing.value === false) {
          localIsProcessing.value = true;
          emit('update:isProcessing', true); // Notify parent to set isProcessing to true
  
          try {
            const params = props.tickers.reduce((acc, ticker, index) => {
              acc[`ticker${index + 1}`] = ticker;
              return acc;
            }, {});
  
            const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/analyze_rittenhouse`, { params });
            analysisReports.value = Object.keys(response.data.reports).map((ticker) => {
              return {
                ticker,
                reports: response.data.reports[ticker],
              };
            });
          } catch (error) {
            console.error('Error fetching Rittenhouse analysis reports:', error);
          } finally {
            localIsProcessing.value = false;
            emit('update:isProcessing', false); // Notify parent to set isProcessing to false
            console.log("Rittenhouse Analysis completed, turning off the flag");
          }
        } else {
          console.log("Button clicked but flag is still:", localIsProcessing.value);
        }
      };
  
      const getFileTypes = () => {
        const fileTypes = new Set();
        analysisReports.value.forEach((reportData) => {
          reportData.reports.forEach((report) => {
            const fileType = extractFileType(report.File);
            fileTypes.add(fileType);
          });
        });
        fileTypes.forEach((fileType) => {
          if (!(fileType in collapsed.value)) {
            collapsed.value[fileType] = true;
          }
        });
        return Array.from(fileTypes);
      };
  
      const extractFileType = (fileName) => {
        const match = fileName.match(/10-[KQ]|8-K|DEF 14A|20-F|6-K/);
        return match ? match[0] : 'Unknown';
      };
  
      const findReportByFileType = (fileType) => {
        for (const reportData of analysisReports.value) {
          const report = reportData.reports.find(
            (report) => extractFileType(report.File) === fileType
          );
          if (report) {
            return report;
          }
        }
        return null;
      };
  
      const getKeywordCountForFileType = (reports, fileType, category, keyword) => {
        const report = reports.find(
          (report) => extractFileType(report.File) === fileType
        );
        return report && report['Keyword Counts'][category] && report['Keyword Counts'][category][keyword]
          ? report['Keyword Counts'][category][keyword]
          : 0;
      };
  
      const getCategoriesForFileType = (fileType) => {
        const report = findReportByFileType(fileType);
        return report ? Object.keys(report['Keyword Counts']) : [];
      };
  
      const getSortedKeywordsForFileType = (fileType, category) => {
        const keywords = getKeywordsForFileType(fileType, category);
        const keywordDataArray = keywords.map((keyword) => {
          const counts = {};
          let totalCount = 0;
  
          analysisReports.value.forEach((reportData) => {
            const count = getKeywordCountForFileType(reportData.reports, fileType, category, keyword);
            counts[reportData.ticker] = count;
            totalCount += count;
          });
  
          return { keyword, counts, totalCount };
        });
  
        return keywordDataArray.sort((a, b) => b.totalCount - a.totalCount);
      };
  
      const getKeywordsForFileType = (fileType, category) => {
        const report = findReportByFileType(fileType);
        return report && report['Keyword Counts'][category]
          ? Object.keys(report['Keyword Counts'][category])
          : [];
      };
  
      const formatFileName = (fileName) => {
        return fileName
          .replace(/^.*[\\/]/, '')  // Remove directory path
          .replace('_complete_submission.txt', '');  // Remove the suffix
      };
  
      return {
        analysisReports,
        collapsed,
        fetchAnalysisReports,
        toggleCollapse,
        getFileTypes,
        extractFileType,
        findReportByFileType,
        getKeywordCountForFileType,
        getCategoriesForFileType,
        getSortedKeywordsForFileType,
        getKeywordsForFileType,
        formatFileName,
        localIsProcessing,
      };
    },
  };
  </script>
  
  <style scoped>
  :root {
    --primary-color: #007bff;
    --header-bg-color: var(--primary-color);
    --header-text-color: #ffffff;
    --row-hover-bg-color: #f1f1f1;
    --row-alt-bg-color: #f9f9f9;
    --border-color: #ddd;
    --font-size: 0.9em;
  }
  .modern-table {
    width: auto;
    border-collapse: collapse;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .modern-table thead {
    background-color: #3a4242;
    color: white;
  }
  
  .modern-table th, .modern-table td {
    padding: auto;
    text-align: left;
    border-bottom: 1px solid #ddd;
    font-size: 0.9em;
  }
  
  .modern-table th {
    position: sticky;
    top: 0;
    z-index: 1;
  }
  
  .modern-table tbody tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  
  .modern-table tbody tr:hover {
    background-color: #f1f1f1;
    transition: background-color 0.2s;
  }
  
  .modern-table td {
    color: #333;
  }
  
    p {
      font-size: 0.9em;
    }
  
    .modern-table th, .modern-table td {
      padding: auto;
      font-size: 0.8em;
    }
  
button {
  background-color: #8bb4e0;
}

button:hover {
  background-color: #468eda;
}
.loading-overlay {
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

  </style>