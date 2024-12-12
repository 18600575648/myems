import React, { Fragment, useEffect, useState, useContext } from 'react';
import {
  Breadcrumb,
  BreadcrumbItem,
  Row,
  Col,
  Card,
  CardBody,
  Button,
  ButtonGroup,
  Form,
  FormGroup,
  Input,
  Label,
  CustomInput,
  Spinner
} from 'reactstrap';
import moment from 'moment';
import loadable from '@loadable/component';
import Cascader from 'rc-cascader';
import MultipleLineChart from '../common/MultipleLineChart';
import { getCookieValue, createCookie, checkEmpty } from '../../../helpers/utils';
import withRedirect from '../../../hoc/withRedirect';
import { withTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import ButtonIcon from '../../common/ButtonIcon';
import { APIBaseURL, settings } from '../../../config';
import { periodTypeOptions } from '../common/PeriodTypeOptions';
import { endOfDay } from 'date-fns';
import AppContext from '../../../context/Context';
import { useLocation } from 'react-router-dom';
import DateRangePickerWrapper from '../common/DateRangePickerWrapper';
import blankPage from '../../../assets/img/generic/blank-page.png';


const DetailedDataTable = loadable(() => import('../common/DetailedDataTable'));

const PhotovoltaicPowerStationReportingRevenue = ({ setRedirect, setRedirectUrl, t }) => {
  let current_moment = moment();
  const location = useLocation();
  const uuid = location.search.split('=')[1];

  useEffect(() => {
    let is_logged_in = getCookieValue('is_logged_in');
    let user_name = getCookieValue('user_name');
    let user_display_name = getCookieValue('user_display_name');
    let user_uuid = getCookieValue('user_uuid');
    let token = getCookieValue('token');
    if (checkEmpty(is_logged_in) || checkEmpty(token) || checkEmpty(user_uuid) || !is_logged_in) {
      setRedirectUrl(`/authentication/basic/login`);
      setRedirect(true);
    } else {
      //update expires time of cookies
      createCookie('is_logged_in', true, settings.cookieExpireTime);
      createCookie('user_name', user_name, settings.cookieExpireTime);
      createCookie('user_display_name', user_display_name, settings.cookieExpireTime);
      createCookie('user_uuid', user_uuid, settings.cookieExpireTime);
      createCookie('token', token, settings.cookieExpireTime);
    }
  });

  // State
  //Query Form
  const [selectedSpaceName, setSelectedSpaceName] = useState(undefined);
  const [selectedSpaceID, setSelectedSpaceID] = useState(undefined);
  const [photovoltaicPowerStationList, setPhotovoltaicPowerStationList] = useState([]);
  const [filteredPhotovoltaicPowerStationList, setFilteredPhotovoltaicPowerStationList] = useState([]);
  const [selectedPhotovoltaicPowerStation, setSelectedPhotovoltaicPowerStation] = useState(undefined);
  const [periodType, setPeriodType] = useState('daily');
  const [cascaderOptions, setCascaderOptions] = useState(undefined);
  const [reportingPeriodDateRange, setReportingPeriodDateRange] = useState([
    current_moment
      .clone()
      .subtract(1, 'weeks')
      .toDate(),
    current_moment.toDate()
  ]);
  const dateRangePickerLocale = {
    sunday: t('sunday'),
    monday: t('monday'),
    tuesday: t('tuesday'),
    wednesday: t('wednesday'),
    thursday: t('thursday'),
    friday: t('friday'),
    saturday: t('saturday'),
    ok: t('ok'),
    today: t('today'),
    yesterday: t('yesterday'),
    hours: t('hours'),
    minutes: t('minutes'),
    seconds: t('seconds'),
    last7Days: t('last7Days'),
    formattedMonthPattern: 'yyyy-MM-dd'
  };
  const dateRangePickerStyle = { display: 'block', zIndex: 10 };
  const { language } = useContext(AppContext);
  // buttons
  const [submitButtonDisabled, setSubmitButtonDisabled] = useState(true);
  const [spinnerHidden, setSpinnerHidden] = useState(true);
  const [exportButtonHidden, setExportButtonHidden] = useState(true);
  const [spaceCascaderHidden, setSpaceCascaderHidden] = useState(false);
  const [resultDataHidden, setResultDataHidden] = useState(true);

  //Results
  const [photovoltaicPowerStationName, setPhotovoltaicPowerStationName] = useState();
  const [photovoltaicPowerStationSerialNumber, setPhotovoltaicPowerStationSerialNumber] = useState();
  const [photovoltaicPowerStationAddress, setPhotovoltaicPowerStationAddress] = useState();
  const [photovoltaicPowerStationPostalCode, setPhotovoltaicPowerStationPostalCode] = useState();
  const [photovoltaicPowerStationRatedCapacity, setPhotovoltaicPowerStationRatedCapacity] = useState();
  const [photovoltaicPowerStationRatedPower, setPhotovoltaicPowerStationRatedPower] = useState();
  const [photovoltaicPowerStationLatitude, setPhotovoltaicPowerStationLatitude] = useState();
  const [photovoltaicPowerStationLongitude, setPhotovoltaicPowerStationLongitude] = useState();

  const [photovoltaicPowerStationBaseLabels, setPhotovoltaicPowerStationBaseLabels] = useState({ a0: [] });
  const [photovoltaicPowerStationBaseData, setPhotovoltaicPowerStationBaseData] = useState({ a0: [] });
  const [photovoltaicPowerStationReportingNames, setPhotovoltaicPowerStationReportingNames] = useState({ a0: '' });
  const [photovoltaicPowerStationReportingUnits, setPhotovoltaicPowerStationReportingUnits] = useState({ a0: '()' });
  const [photovoltaicPowerStationReportingSubtotals, setPhotovoltaicPowerStationReportingSubtotals] = useState({
    a0: (0).toFixed(2)
  });
  const [photovoltaicPowerStationReportingLabels, setPhotovoltaicPowerStationReportingLabels] = useState({ a0: [] });
  const [photovoltaicPowerStationReportingData, setPhotovoltaicPowerStationReportingData] = useState({ a0: [] });
  const [photovoltaicPowerStationReportingOptions, setPhotovoltaicPowerStationReportingOptions] = useState([]);

  const [timeOfUseDataTableData, setTimeOfUseDataTableData] = useState([]);
  const [detailedDataTableData, setDetailedDataTableData] = useState([]);
  const [detailedDataTableColumns, setDetailedDataTableColumns] = useState([
    { dataField: 'startdatetime', text: t('Datetime'), sort: true }
  ]);

  const [excelBytesBase64, setExcelBytesBase64] = useState(undefined);

  useEffect(() => {
    let isResponseOK = false;
    setSpaceCascaderHidden(false);
    fetch(APIBaseURL + '/spaces/tree', {
      method: 'GET',
      headers: {
        'Content-type': 'application/json',
        'User-UUID': getCookieValue('user_uuid'),
        Token: getCookieValue('token')
      },
      body: null
    })
      .then(response => {
        console.log(response);
        if (response.ok) {
          isResponseOK = true;
        }
        return response.json();
      })
      .then(json => {
        console.log(json);
        if (isResponseOK) {
          // rename keys
          json = JSON.parse(
            JSON.stringify([json])
              .split('"id":')
              .join('"value":')
              .split('"name":')
              .join('"label":')
          );
          setCascaderOptions(json);
          setSelectedSpaceName([json[0]].map(o => o.label));
          setSelectedSpaceID([json[0]].map(o => o.value));
          // get PhotovoltaicPowerStations by root Space ID
          let isResponseOK = false;
          fetch(APIBaseURL + '/spaces/' + [json[0]].map(o => o.value) + '/photovoltaicpowerstations', {
            method: 'GET',
            headers: {
              'Content-type': 'application/json',
              'User-UUID': getCookieValue('user_uuid'),
              Token: getCookieValue('token')
            },
            body: null
          })
            .then(response => {
              if (response.ok) {
                isResponseOK = true;
              }
              return response.json();
            })
            .then(json => {
              if (isResponseOK) {
                json = JSON.parse(
                  JSON.stringify([json])
                    .split('"id":')
                    .join('"value":')
                    .split('"name":')
                    .join('"label":')
                );
                console.log(json);
                setPhotovoltaicPowerStationList(json[0]);
                setFilteredPhotovoltaicPowerStationList(json[0]);
                if (json[0].length > 0) {
                  setSelectedPhotovoltaicPowerStation(json[0][0].value);
                  // enable submit button
                  setSubmitButtonDisabled(false);
                } else {
                  setSelectedPhotovoltaicPowerStation(undefined);
                  // disable submit button
                  setSubmitButtonDisabled(true);
                }
              } else {
                toast.error(t(json.description));
              }
            })
            .catch(err => {
              console.log(err);
            });
          // end of get PhotovoltaicPowerStations by root Space ID
        } else {
          toast.error(t(json.description));
        }
      })
      .catch(err => {
        console.log(err);
      });
  }, []);

  const loadData = url => {
    // disable submit button
    setSubmitButtonDisabled(true);
    // show spinner
    setSpinnerHidden(false);
    // hide export button
    setExportButtonHidden(true);
    // hide result data
    setResultDataHidden(true);

    // Reinitialize tables
    setTimeOfUseDataTableData([]);
    setDetailedDataTableData([]);

    let isResponseOK = false;
    fetch(url, {
      method: 'GET',
      headers: {
        'Content-type': 'application/json',
        'User-UUID': getCookieValue('user_uuid'),
        Token: getCookieValue('token')
      },
      body: null
    })
      .then(response => {
        if (response.ok) {
          isResponseOK = true;
        }
        return response.json();
      })
      .then(json => {
        if (isResponseOK) {
          console.log(json);
          setPhotovoltaicPowerStationName(json['photovoltaic_power_station']['name']);
          setPhotovoltaicPowerStationSerialNumber(json['photovoltaic_power_station']['serial_number']);
          setPhotovoltaicPowerStationAddress(json['photovoltaic_power_station']['address']);
          setPhotovoltaicPowerStationPostalCode(json['photovoltaic_power_station']['postal_code']);
          setPhotovoltaicPowerStationRatedCapacity(json['photovoltaic_power_station']['rated_capacity']);
          setPhotovoltaicPowerStationRatedPower(json['photovoltaic_power_station']['rated_power']);
          setPhotovoltaicPowerStationLatitude(json['photovoltaic_power_station']['latitude']);
          setPhotovoltaicPowerStationLongitude(json['photovoltaic_power_station']['longitude']);

          let base_and_reporting_names = {};
          json['reporting_period']['names'].forEach((currentValue, index) => {
            base_and_reporting_names['a' + index] = currentValue;
          });
          setPhotovoltaicPowerStationReportingNames(base_and_reporting_names);

          let base_and_reporting_units = {};
          json['reporting_period']['units'].forEach((currentValue, index) => {
            base_and_reporting_units['a' + index] = '(' + currentValue + ')';
          });
          setPhotovoltaicPowerStationReportingUnits(base_and_reporting_units);

          let reporting_timestamps = {};
          json['reporting_period']['timestamps'].forEach((currentValue, index) => {
            reporting_timestamps['a' + index] = currentValue;
          });
          setPhotovoltaicPowerStationReportingLabels(reporting_timestamps);

          let reporting_values = {};
          json['reporting_period']['values'].forEach((currentValue, index) => {
            reporting_values['a' + index] = currentValue;
          });
          console.log(reporting_values);
          setPhotovoltaicPowerStationReportingData(reporting_values);

          let reporting_subtotals = {};
          json['reporting_period']['subtotals'].forEach((currentValue, index) => {
            reporting_subtotals['a' + index] = currentValue.toFixed(2);
          });
          setPhotovoltaicPowerStationReportingSubtotals(reporting_subtotals);

          let options = [];
          json['reporting_period']['names'].forEach((currentValue, index) => {
            let unit = json['reporting_period']['units'][index];
            options.push({ value: 'a' + index, label: currentValue + ' (' + unit + ')' });
          });
          setPhotovoltaicPowerStationReportingOptions(options);
          setExcelBytesBase64(json['excel_bytes_base64']);


          let detailed_column_list = [];

          detailed_column_list.push({
            dataField: 'reportingPeriodDatetime',
            text: t('Datetime'),
            sort: true
          });

          json['reporting_period']['names'].forEach((currentValue, index) => {
            let unit = json['reporting_period']['units'][index];
            detailed_column_list.push({
              dataField: 'b' + index,
              text: currentValue + ' (' + unit + ')',
              sort: true,
              formatter: function(decimalValue) {
                if (typeof decimalValue === 'number') {
                  return decimalValue.toFixed(2);
                } else {
                  return null;
                }
              }
            });
          });
          setDetailedDataTableColumns(detailed_column_list);

          let time_of_use_value_list = [];
          // toppeak
          let time_of_use_value = {};
          time_of_use_value['id'] = time_of_use_value_list.length;

          time_of_use_value['reportingPeriodDatetime'] = '尖';
          json['reporting_period']['toppeaks'].forEach((currentValue, index) => {
            time_of_use_value['b' + index] = currentValue;
          });
          time_of_use_value_list.push(time_of_use_value);

          // onpeak
          time_of_use_value = {};
          time_of_use_value['id'] = time_of_use_value_list.length;

          time_of_use_value['reportingPeriodDatetime'] = '峰';
          json['reporting_period']['onpeaks'].forEach((currentValue, index) => {
            time_of_use_value['b' + index] = currentValue;
          });
          time_of_use_value_list.push(time_of_use_value);

          //midpeak
          time_of_use_value = {};
          time_of_use_value['id'] = time_of_use_value_list.length;

          time_of_use_value['reportingPeriodDatetime'] = '平';
          json['reporting_period']['midpeaks'].forEach((currentValue, index) => {
            time_of_use_value['b' + index] = currentValue;
          });
          time_of_use_value_list.push(time_of_use_value);

          //offpeak
          time_of_use_value = {};
          time_of_use_value['id'] = time_of_use_value_list.length;

          time_of_use_value['reportingPeriodDatetime'] = '谷';
          json['reporting_period']['offpeaks'].forEach((currentValue, index) => {
            time_of_use_value['b' + index] = currentValue;
          });
          time_of_use_value_list.push(time_of_use_value);

          time_of_use_value = {};
          time_of_use_value['id'] = time_of_use_value_list.length;

          time_of_use_value['reportingPeriodDatetime'] = t('Subtotal');
          json['reporting_period']['subtotals'].forEach((currentValue, index) => {
            time_of_use_value['b' + index] = currentValue;
          });
          time_of_use_value_list.push(time_of_use_value);
          setTimeout(() => {
            setTimeOfUseDataTableData(time_of_use_value_list);
          }, 0);

          let detailed_value_list = [];
          if (json['reporting_period']['timestamps'].length > 0) {
            const max_timestamps_length = json['reporting_period']['timestamps'][0].length;
            for (let index = 0; index < max_timestamps_length; index++) {
              let detailed_value = {};
              detailed_value['id'] = index;

              detailed_value['reportingPeriodDatetime'] =
                index < json['reporting_period']['timestamps'][0].length
                  ? json['reporting_period']['timestamps'][0][index]
                  : null;
              json['reporting_period']['values'].forEach((currentValue, energyCategoryIndex) => {
                detailed_value['b' + energyCategoryIndex] =
                  index < json['reporting_period']['values'][energyCategoryIndex].length
                    ? json['reporting_period']['values'][energyCategoryIndex][index]
                    : null;
              });
              detailed_value_list.push(detailed_value);
            }

            let detailed_value = {};
            detailed_value['id'] = detailed_value_list.length;

            detailed_value['reportingPeriodDatetime'] = t('Subtotal');
            json['reporting_period']['subtotals'].forEach((currentValue, index) => {
              detailed_value['b' + index] = currentValue;
            });
            detailed_value_list.push(detailed_value);
            setTimeout(() => {
              setDetailedDataTableData(detailed_value_list);
            }, 0);
          }

          // enable submit button
          setSubmitButtonDisabled(false);
          // hide spinner
          setSpinnerHidden(true);
          // show export button
          setExportButtonHidden(false);
          // show result data
          setResultDataHidden(false);
        } else {
          toast.error(t(json.description));
          setSpinnerHidden(true);
          setSubmitButtonDisabled(false);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };
  const labelClasses = 'ls text-uppercase text-600 font-weight-semi-bold mb-0';

  let onSpaceCascaderChange = (value, selectedOptions) => {
    setSelectedSpaceName(selectedOptions.map(o => o.label).join('/'));
    setSelectedSpaceID(value[value.length - 1]);

    let isResponseOK = false;
    fetch(APIBaseURL + '/spaces/' + value[value.length - 1] + '/photovoltaicpowerstations', {
      method: 'GET',
      headers: {
        'Content-type': 'application/json',
        'User-UUID': getCookieValue('user_uuid'),
        Token: getCookieValue('token')
      },
      body: null
    })
      .then(response => {
        if (response.ok) {
          isResponseOK = true;
        }
        return response.json();
      })
      .then(json => {
        if (isResponseOK) {
          json = JSON.parse(
            JSON.stringify([json])
              .split('"id":')
              .join('"value":')
              .split('"name":')
              .join('"label":')
          );
          console.log(json);
          setPhotovoltaicPowerStationList(json[0]);
          setFilteredPhotovoltaicPowerStationList(json[0]);
          if (json[0].length > 0) {
            setSelectedPhotovoltaicPowerStation(json[0][0].value);
            // enable submit button
            setSubmitButtonDisabled(false);
          } else {
            setSelectedPhotovoltaicPowerStation(undefined);
            // disable submit button
            setSubmitButtonDisabled(true);
          }
        } else {
          toast.error(t(json.description));
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  const onSearchPhotovoltaicPowerStation = ({ target }) => {
    const keyword = target.value.toLowerCase();
    const filteredResult = photovoltaicPowerStationList.filter(photovoltaicPowerStation =>
      photovoltaicPowerStation.label.toLowerCase().includes(keyword)
    );
    setFilteredPhotovoltaicPowerStationList(keyword.length ? filteredResult : photovoltaicPowerStationList);
    if (filteredResult.length > 0) {
      setSelectedPhotovoltaicPowerStation(filteredResult[0].value);
      // enable submit button
      setSubmitButtonDisabled(false);
    } else {
      setSelectedPhotovoltaicPowerStation(undefined);
      // disable submit button
      setSubmitButtonDisabled(true);
    }
    let customInputTarget = document.getElementById('photovoltaicPowerStationSelect');
    customInputTarget.value = filteredResult[0].value;
  };

  // Callback fired when value changed
  let onReportingPeriodChange = DateRange => {
    if (DateRange == null) {
      setReportingPeriodDateRange([null, null]);
    } else {
      if (moment(DateRange[1]).format('HH:mm:ss') === '00:00:00') {
        // if the user did not change time value, set the default time to the end of day
        DateRange[1] = endOfDay(DateRange[1]);
      }
      setReportingPeriodDateRange([DateRange[0], DateRange[1]]);
      const dateDifferenceInSeconds = moment(DateRange[1]).valueOf() / 1000 - moment(DateRange[0]).valueOf() / 1000;
      if (periodType === 'hourly') {
        if (dateDifferenceInSeconds > 3 * 365 * 24 * 60 * 60) {
          // more than 3 years
          setPeriodType('yearly');
          document.getElementById('periodType').value = 'yearly';
        } else if (dateDifferenceInSeconds > 6 * 30 * 24 * 60 * 60) {
          // more than 6 months
          setPeriodType('monthly');
          document.getElementById('periodType').value = 'monthly';
        } else if (dateDifferenceInSeconds > 30 * 24 * 60 * 60) {
          // more than 30 days
          setPeriodType('daily');
          document.getElementById('periodType').value = 'daily';
        }
      } else if (periodType === 'daily') {
        if (dateDifferenceInSeconds >= 3 * 365 * 24 * 60 * 60) {
          // more than 3 years
          setPeriodType('yearly');
          document.getElementById('periodType').value = 'yearly';
        } else if (dateDifferenceInSeconds >= 6 * 30 * 24 * 60 * 60) {
          // more than 6 months
          setPeriodType('monthly');
          document.getElementById('periodType').value = 'monthly';
        }
      } else if (periodType === 'monthly') {
        if (dateDifferenceInSeconds >= 3 * 365 * 24 * 60 * 60) {
          // more than 3 years
          setPeriodType('yearly');
          document.getElementById('periodType').value = 'yearly';
        }
      }
    }
  };

  // Callback fired when value clean
  let onReportingPeriodClean = event => {
    setReportingPeriodDateRange([null, null]);
  };

  // Handler
  const handleSubmit = e => {
    e.preventDefault();
    console.log('handleSubmit');
    console.log(selectedSpaceID);
    console.log(selectedPhotovoltaicPowerStation);
    console.log(periodType);
    console.log(moment(reportingPeriodDateRange[0]).format('YYYY-MM-DDTHH:mm:ss'));
    console.log(moment(reportingPeriodDateRange[1]).format('YYYY-MM-DDTHH:mm:ss'));

    let url =
      APIBaseURL +
      '/reports/photovoltaicpowerstationreportingrevenue?' +
      'id=' +
      selectedPhotovoltaicPowerStation +
      '&periodtype=' +
      periodType +
      '&reportingperiodstartdatetime=' +
      moment(reportingPeriodDateRange[0]).format('YYYY-MM-DDTHH:mm:ss') +
      '&reportingperiodenddatetime=' +
      moment(reportingPeriodDateRange[1]).format('YYYY-MM-DDTHH:mm:ss') +
      '&language=' +
      language;
    loadData(url);
  };

  const handleExport = e => {
    e.preventDefault();
    const mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    const fileName = 'photovoltaicPowerStationreproting.xlsx';
    var fileUrl = 'data:' + mimeType + ';base64,' + excelBytesBase64;
    fetch(fileUrl)
      .then(response => response.blob())
      .then(blob => {
        var link = window.document.createElement('a');
        link.href = window.URL.createObjectURL(blob, { type: mimeType });
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
  };

  return (
    <Fragment>
      <Card className="bg-light mb-3">
        <CardBody className="p-3">
          <Form onSubmit={handleSubmit}>
            <Row form>
              <Col xs={6} sm={3} hidden={spaceCascaderHidden}>
                <FormGroup className="form-group">
                  <Label className={labelClasses} for="space">
                    {t('Space')}
                  </Label>
                  <br />
                  <Cascader
                    options={cascaderOptions}
                    onChange={onSpaceCascaderChange}
                    changeOnSelect
                    expandTrigger="hover"
                  >
                    <Input bsSize="sm" value={selectedSpaceName || ''} readOnly />
                  </Cascader>
                </FormGroup>
              </Col>
              <Col xs="auto">
                <FormGroup>
                  <Label className={labelClasses} for="photovoltaicPowerStationSelect">
                    {t('Photovoltaic Power Station')}
                  </Label>

                  <Form inline>
                    <CustomInput
                      type="select"
                      id="photovoltaicPowerStationSelect"
                      name="photovoltaicPowerStationSelect"
                      bsSize="sm"
                      onChange={({ target }) => setSelectedPhotovoltaicPowerStation(target.value)}
                    >
                      {filteredPhotovoltaicPowerStationList.map((photovoltaicPowerStation, index) => (
                        <option value={photovoltaicPowerStation.value} key={photovoltaicPowerStation.value}>
                          {photovoltaicPowerStation.label}
                        </option>
                      ))}
                    </CustomInput>
                  </Form>
                </FormGroup>
              </Col>
              <Col xs="auto">
                <FormGroup>
                  <Label className={labelClasses} for="periodType">
                    {t('Period Types')}
                  </Label>
                  <CustomInput
                    type="select"
                    id="periodType"
                    name="periodType"
                    bsSize="sm"
                    defaultValue="daily"
                    onChange={({ target }) => setPeriodType(target.value)}
                  >
                    {periodTypeOptions.map((periodType, index) => (
                      <option value={periodType.value} key={periodType.value}>
                        {t(periodType.label)}
                      </option>
                    ))}
                  </CustomInput>
                </FormGroup>
              </Col>
              <Col xs={6} sm={3}>
                <FormGroup className="form-group">
                  <Label className={labelClasses} for="reportingPeriodDateRangePicker">
                    {t('Reporting Period')}
                  </Label>
                  <br />
                  <DateRangePickerWrapper
                    id="reportingPeriodDateRangePicker"
                    format="yyyy-MM-dd HH:mm:ss"
                    value={reportingPeriodDateRange}
                    onChange={onReportingPeriodChange}
                    size="sm"
                    style={dateRangePickerStyle}
                    onClean={onReportingPeriodClean}
                    locale={dateRangePickerLocale}
                    placeholder={t('Select Date Range')}
                  />
                </FormGroup>
              </Col>
              <Col xs="auto">
                <FormGroup>
                  <br />
                  <ButtonGroup id="submit">
                    <Button size="sm" color="success" disabled={submitButtonDisabled}>
                      {t('Submit')}
                    </Button>
                  </ButtonGroup>
                </FormGroup>
              </Col>
              <Col xs="auto">
                <FormGroup>
                  <br />
                  <Spinner color="primary" hidden={spinnerHidden} />
                </FormGroup>
              </Col>
              <Col xs="auto">
                <br />
                <ButtonIcon
                  icon="external-link-alt"
                  transform="shrink-3 down-2"
                  color="falcon-default"
                  size="sm"
                  hidden={exportButtonHidden}
                  onClick={handleExport}
                >
                  {t('Export')}
                </ButtonIcon>
              </Col>
            </Row>
          </Form>
        </CardBody>
      </Card>
      <div  style={{ visibility: resultDataHidden ? 'visible' : 'hidden', display: resultDataHidden ? '': 'none' }}>
          <img className="img-fluid" src={blankPage} alt="" />
      </div>
      <div style={{ visibility: resultDataHidden ? 'hidden' : 'visible', display: resultDataHidden ? 'none': ''  }}>
        <DetailedDataTable
          data={timeOfUseDataTableData}
          title='分时数据'
          columns={detailedDataTableColumns}
          pagesize={50}
          hidden={true}
        />
        <DetailedDataTable
          data={detailedDataTableData}
          title={t('Detailed Data')}
          columns={detailedDataTableColumns}
          pagesize={50}
          hidden={true}
        />
      </div>
    </Fragment>
  );
};

export default withTranslation()(withRedirect(PhotovoltaicPowerStationReportingRevenue));
