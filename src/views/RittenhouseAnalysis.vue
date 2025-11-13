<template>
  <div v-if="tickers.length > 0">
    <div class="terminal">
      <span>eacsa></span> analyze sentiment:
      

                     <button 
                :disabled="loading.isLoading" 
                @click="fetchAnalysisReports" 
                class="buttons">
            {{loading['isLoading'] ? 'generating report': 'GO'}}
            </button>
    </div>


    <div v-if="analysisReports.length && !localIsProcessing">
      <button @click="toggleCollapse" class="buttons">
        ⟬⟬ expand/collapse ⟭⟭
      </button>
      <div v-if="compact" style="display: flex;flex-flow: row wrap; gap: 0.5rem;">
        <p>
              Polarity: Measures the tone of the text. Values range from –1 (negative) to +1 (positive).
              Subjectivity: Measures how factual or opinion-based the text is.Values range from 0 (objective) to 1 (subjective).
        </p>
          <div v-for="reportData in analysisReports" :key="reportData.ticker" style="display: flex;">
            <div v-for="report in reportData['reports']" :key="report.File" class="terminal"  style=" border: solid 1px blue;width: auto; padding: 10px;">
            <span>report type: {{ extractFileType(report['File']) }} </span>
            <br>polarity: {{ report['Sentiment Polarity'].toFixed(2) }}
            subjectivity: {{ report['Sentiment Subjectivity'].toFixed(2) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  
</template>

<script>
import axios from 'axios';
import { watch, ref } from 'vue';
import { useLoadingStore } from '@/stores/loadingStore';

export default {
  props: {
    tickers: {
      type: Array
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
    const compact = ref(false);
    const localIsProcessing = ref(props.isProcessing);
    const loading = useLoadingStore();
    const toggleCollapse = () => {
      compact.value = !compact.value;
    };


    watch(
      () => props.tickers,
      (newTickers) => {
        if (newTickers.length) {
          fetchAnalysisReports(newTickers);
        }
      },
      { immediate: true }
    );

    const fetchAnalysisReports = async () => {

      loading.startLoading();
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
        loading.stopLoading();

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
      compact,
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
      loading
    };
  },
};
</script>

<style scoped></style>