import React, { useState, useContext, useEffect, useRef } from 'react';
import { Row, Col, Card, CardBody, CustomInput } from 'reactstrap';
import { rgbaColor, themeColors, isIterableArray } from '../../../helpers/utils';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { withTranslation } from 'react-i18next';
import { Chart } from 'react-chartjs-2';
import AppContext from '../../../context/Context';
import ChartDataLabels from 'chartjs-plugin-datalabels';


ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  Tooltip,
  Legend,
);

const MultiTrendChart = ({
  reportingTitle,
  baseTitle,
  reportingTooltipTitle,
  baseTooltipTitle,
  reportingLabels,
  baseLabels,
  reportingData,
  baseData,
  rates,
  options,
  t
}) => {
  const [selectedLabel, setSelectedLabel] = useState('a0');
  const [option, setOption] = useState('a0');
  const { isDark } = useContext(AppContext);
  const chartRef = useRef(null);
  const [lineData, setLineData] = useState({
    datasets: [],
  });  
  useEffect(() => {
    const chart = chartRef.current;
    if (chart) {
      const ctx = chart.ctx;
      const gradientFill = isDark
        ? ctx.createLinearGradient(0, 0, 0, ctx.canvas.height)
        : ctx.createLinearGradient(0, 0, 0, 250);
      gradientFill.addColorStop(0, isDark ? 'rgba(44,123,229, 0.5)' : 'rgba(255, 255, 255, 0.3)');
      gradientFill.addColorStop(1, isDark ? 'transparent' : 'rgba(255, 255, 255, 0)');
      
      const chartData = {
        datasets: [{
            data: rates,
            borderColor: rgbaColor(isDark ? themeColors.primary : '#000', 0.8) ,
            backgroundColor: gradientFill,
            type: 'line',
            yAxisID: 'y1',
            tooltip: {
              callbacks: {
                label: function(context){
                  return context.raw + '%';
                }
              }
            },
            datalabels: {
              formatter: function(value, context) {
                return value + '%';
              },
              color: isDark ? themeColors.light : themeColors.dark,
              align: 'end',
              anchor: 'end',
              display: function(){
                return rates.length <= 20 ? true : false;
              }
            }
          },{
            label: baseTitle,
            data: baseData[option],
            backgroundColor: '#4463b6',
            stack: "base",
            tension: 0.4,
            datalabels: {
              display: function(context){
                return false;
               }
            },
          },{
            label: reportingTitle,
            data: reportingData[option],
            backgroundColor: '#e87637',
            stack: "reporting",
            tension: 0.4,
            datalabels: {
              display: function(context){
                return false;
               }
            },
          },],
        labels: reportingLabels[selectedLabel],
      };
      setLineData(chartData);
    }
  }, [baseData, reportingData, option, baseLabels, reportingLabels, rates]);

  const config = {
    plugins: [ChartDataLabels],
    options: {
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
            xPadding: 20,
            yPadding: 10,
            displayColors: false,
            callbacks: {
            title: function(context){
                if (context[0].datasetIndex - 1) {
                    return `${reportingLabels[selectedLabel][context[0].dataIndex]}`;
                } else {
                    return `${baseLabels[selectedLabel][context[0].dataIndex]}`;
                }
            },    
            label: function(context){
                if (context.datasetIndex - 1) {
                    return `${reportingTooltipTitle} - ${context.raw}`;
                } else {
                    return `${baseTooltipTitle} - ${context.raw}`;
                }
            }
            }
        },
      },
      interaction: {
        intersect: false,
        mode: 'x',
        },
      scales: {
        x: {
            display: true,
            ticks: {
                fontColor: rgbaColor('#fff', 0.8),
                fontStyle: 600,
                color: isDark ? themeColors.light : themeColors.dark
            },
            stacked: true,
        },
        y: {
            display: true,
            gridLines: {
                color: rgbaColor('#000', 0.1)
            },
            ticks: {
              color: isDark ? themeColors.light : themeColors.dark
            },
            stack: true,
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: {
            drawOnChartArea: false,
          },
          suggestedMax: 100,
          ticks: {
            callback: function(value, index, ticks){
              return value + '%';
            },
            color: isDark ? themeColors.light : themeColors.dark
          }
        },
      },
      hover: { mode: 'label' },
    }
  };

  return (
    <Card className="mb-3">
      <CardBody className="rounded-soft">
        <Row className="text-white align-items-center no-gutters">
          <Col>
            <h4 className="text-lightSlateGray mb-0">{reportingTitle}</h4>
            <p className="fs--1 font-weight-semi-bold">
              {baseTitle}
            </p>
          </Col>
          {isIterableArray(options) &&
            <Col xs="auto" className="d-none d-sm-block">
              <CustomInput
                id="ddd"
                type="select"
                bsSize="sm"
                className="mb-3 shadow"
                value={option}
                onChange={({ target }) => {setOption(target.value); setSelectedLabel(target.value); chartRef.current.update();}}
              >
                {options.map(({ value, label }) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
              </CustomInput>
            </Col>
          }
        </Row>
        <Chart ref={chartRef} type="bar" data={lineData} options={config.options} plugins={config.plugins} width={1618} height={218} />
      </CardBody> 
    </Card>
  );
};

export default withTranslation()(MultiTrendChart);

