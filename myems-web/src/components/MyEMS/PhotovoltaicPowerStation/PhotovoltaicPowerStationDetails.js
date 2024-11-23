import React, { Fragment, useState, useEffect } from 'react';
import {
  Button,
  ButtonGroup,
  Card,
  CardBody,
  Col,
  CustomInput,
  CardTitle,
  CardText,
  Form,
  FormGroup,
  Input,
  Label,
  Row,
  Table,
  Spinner,
  Nav,
  NavItem,
  NavLink,
  TabContent,
  TabPane
} from 'reactstrap';
import Cascader from 'rc-cascader';
import FalconCardHeader from '../../common/FalconCardHeader';
import MultipleLineChart from '../common/MultipleLineChart';
import { getCookieValue, createCookie, checkEmpty } from '../../../helpers/utils';
import withRedirect from '../../../hoc/withRedirect';
import { withTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { v4 as uuidv4 } from 'uuid';
import { APIBaseURL, settings } from '../../../config';
import useInterval from '../../../hooks/useInterval';
import { useLocation } from 'react-router-dom';
import Datetime from 'react-datetime';
import { isIterableArray } from '../../../helpers/utils';
import classNames from 'classnames';
import ScheduleDetails from './ScheduleDetails';
import BMSDetails from './BMSDetails';
import FirecontrolDetails from './FirecontrolDetails';
import PCSDetails from './PCSDetails';
import HVACDetails from './HVACDetails';
import MeterDetails from './MeterDetails';
import DeviceStatusDetails from './DeviceStatusDetails';
import blankPage from '../../../assets/img/generic/blank-page.png';


const PhotovoltaicPowerStationDetails = ({ setRedirect, setRedirectUrl, t }) => {
  const location = useLocation();
  const uuid = location.search.split('=')[1];
  const photovoltaicPowerStationUUID = location.search.split('=')[1];

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

  useEffect(() => {
    let timer = setInterval(() => {
      let is_logged_in = getCookieValue('is_logged_in');
      if (is_logged_in === null || !is_logged_in) {
        setRedirectUrl(`/authentication/basic/login`);
        setRedirect(true);
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [setRedirect, setRedirectUrl]);

  const [activeTabLeft, setActiveTabLeft] = useState('1');
  const toggleTabLeft = tab => {
    if (activeTabLeft !== tab) setActiveTabLeft(tab);

  };

  const [activeTabRight, setActiveTabRight] = useState('1');
  const toggleTabRight = tab => {
    if (activeTabRight !== tab) setActiveTabRight(tab);
  };

  const [activeTabBottom, setActiveTabBottom] = useState('1');

  // State
  const [selectedSpaceName, setSelectedSpaceName] = useState(undefined);
  const [selectedSpaceID, setSelectedSpaceID] = useState(undefined);
  const [stationList, setStationList] = useState([]);
  const [filteredStationList, setFilteredStationList] = useState([]);
  const [selectedStation, setSelectedStation] = useState(undefined);
  const [cascaderOptions, setCascaderOptions] = useState(undefined);

  // buttons
  const [submitButtonDisabled, setSubmitButtonDisabled] = useState(true);
  const [submitButtonHidden, setSubmitButtonHidden] = useState(true);
  const [spinnerHidden, setSpinnerHidden] = useState(true);
  const [spaceCascaderHidden, setSpaceCascaderHidden] = useState(false);
  const [resultDataHidden, setResultDataHidden] = useState(true);

  //Results
  const [photovoltaicPowerStationName, setPhotovoltaicPowerStationName] = useState();
  const [photovoltaicPowerStationAddress, setPhotovoltaicPowerStationAddress] = useState();
  const [photovoltaicPowerStationPostalCode, setPhotovoltaicPowerStationPostalCode] = useState();
  const [photovoltaicPowerStationRatedCapacity, setPhotovoltaicPowerStationRatedCapacity] = useState();
  const [photovoltaicPowerStationRatedPower, setPhotovoltaicPowerStationRatedPower] = useState();
  const [photovoltaicPowerStationSVG, setPhotovoltaicPowerStationSVG] = useState();
  const [gatewayStatus, setGatewayStatus] = useState();
  const [PCSStatus, setPCSStatus] = useState();
  const [BMSStatus, setBMSStatus] = useState();
  const [HVACStatus, setHVACStatus] = useState();
  const [gridMeterStatus, setGridMeterStatus] = useState();
  const [loadMeterStatus, setLoadMeterStatus] = useState();


  const [todayChargeEnergyValue, setTodayChargeEnergyValue] = useState();
  const [todayDischargeEnergyValue, setTodayDischargeEnergyValue] = useState();
  const [totalChargeEnergyValue, setTotalChargeEnergyValue] = useState();
  const [totalDischargeEnergyValue, setTotalDischargeEnergyValue] = useState();
  const [totalEfficiency, setTotalEfficiency] = useState();

  const [todayChargeRevenueValue, setTodayChargeRevenueValue] = useState();
  const [todayDischargeRevenueValue, setTodayDischargeRevenueValue] = useState();
  const [totalChargeRevenueValue, setTotalChargeRevenueValue] = useState();
  const [totalDischargeRevenueValue, setTotalDischargeRevenueValue] = useState();

  const [scheduleXaxisData, setScheduleXaxisData] = useState();
  const [scheduleSeriesName, setScheduleSeriesName] = useState();
  const [scheduleSeriesData, setScheduleSeriesData] = useState();
  const [scheduleMarkAreaData, setScheduleMarkAreaData] = useState();

  const [parameterLineChartLabels, setParameterLineChartLabels] = useState([]);
  const [parameterLineChartData, setParameterLineChartData] = useState({});
  const [parameterLineChartOptions, setParameterLineChartOptions] = useState([]);


  const [BMSDetailsList, setBMSDetailsList] = useState([]);
  const [firecontrolDetailsList, setFirecontrolDetailsList] = useState([]);
  const [HVACDetailsList, setHVACDetailsList] = useState([]);
  const [PCSDetailsList, setPCSDetailsList] = useState([]);
  const [meterDetailsList, setMeterDetailsList] = useState([]);


  useEffect(() => {
    console.log("uuid:");
    console.log(uuid);
    if (uuid === null || !uuid) {
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
            // get Photovoltaic  Power Stations by root Space ID
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
                  setStationList(json[0]);
                  setFilteredStationList(json[0]);
                  if (json[0].length > 0) {
                    setSelectedStation(json[0][0].value);
                    // enable submit button
                    setSubmitButtonDisabled(false);
                    setSubmitButtonHidden(false);
                  } else {
                    setSelectedStation(undefined);
                    // disable submit button
                    setSubmitButtonDisabled(true);
                    setSubmitButtonHidden(true);
                  }
                } else {
                  toast.error(t(json.description));
                }
              })
              .catch(err => {
                console.log(err);
              });
            // end of get Photovoltaic  Power Stations by root Space ID
          } else {
            toast.error(t(json.description));
          }
        })
        .catch(err => {
          console.log(err);
        });
    } else {
        setSpaceCascaderHidden(true);
        loadData(APIBaseURL + '/reports/photovoltaicpowerstationdetails?uuid=' + photovoltaicPowerStationUUID)
      }
  }, [photovoltaicPowerStationUUID]);

  const loadData = url => {
    console.log('url:' + url);
    // disable submit button
    setSubmitButtonDisabled(true);
    // show spinner
    setSpinnerHidden(false);
    // hide result data
    setResultDataHidden(true);

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
          if (uuid !== null && uuid) {
            setFilteredStationList([{ id: json['photovoltaic_power_station']['id'], label: json['photovoltaic_power_station']['name'] }]);
            setSelectedStation(json['photovoltaic_power_station']['id']);
          }
          setPhotovoltaicPowerStationName(json['photovoltaic_power_station']['name']);
          setPhotovoltaicPowerStationAddress(json['photovoltaic_power_station']['address']);
          setPhotovoltaicPowerStationPostalCode(json['photovoltaic_power_station']['postal_code']);
          setPhotovoltaicPowerStationRatedCapacity(json['photovoltaic_power_station']['rated_capacity']);
          setPhotovoltaicPowerStationRatedPower(json['photovoltaic_power_station']['rated_power']);
          setPhotovoltaicPowerStationSVG({ __html: json['photovoltaic_power_station']['svg'] });

          setTodayChargeEnergyValue(json['energy_indicators']['today_charge_energy_value']);
          setTodayDischargeEnergyValue(json['energy_indicators']['today_discharge_energy_value']);
          setTotalChargeEnergyValue(json['energy_indicators']['total_charge_energy_value']);
          setTotalDischargeEnergyValue(json['energy_indicators']['total_discharge_energy_value']);

          if (json['energy_indicators']['total_charge_energy_value'] > 0) {
            setTotalEfficiency((100 * json['energy_indicators']['total_discharge_energy_value'] / json['energy_indicators']['total_charge_energy_value']).toFixed(2))
          } else {
            setTotalEfficiency(0)
          }

          setTodayChargeRevenueValue(json['revenue_indicators']['today_charge_revenue_value']);
          setTodayDischargeRevenueValue(json['revenue_indicators']['today_discharge_revenue_value']);
          setTotalChargeRevenueValue(json['revenue_indicators']['total_charge_revenue_value']);
          setTotalDischargeRevenueValue(json['revenue_indicators']['total_discharge_revenue_value']);

          let timestamps = {};
          json['parameters']['timestamps'].forEach((currentValue, index) => {
            timestamps['a' + index] = currentValue;
          });
          setParameterLineChartLabels(timestamps);

          let values = {};
          json['parameters']['values'].forEach((currentValue, index) => {
            values['a' + index] = currentValue;
          });
          setParameterLineChartData(values);

          let names = [];
          json['parameters']['names'].forEach((currentValue, index) => {
            names.push({ value: 'a' + index, label: currentValue });
          });
          setParameterLineChartOptions(names);

          // enable submit button
          setSubmitButtonDisabled(false);
          // hide spinner
          setSpinnerHidden(true);
          // show result data
          setResultDataHidden(false);
        } else {
          toast.error(t(json.description));
          // enable submit button
          setSubmitButtonDisabled(false);
          // hide spinner
          setSpinnerHidden(true);
        }
      })
      .catch(err => {
        console.log(err);
      });
  }
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
          setStationList(json[0]);
          setFilteredStationList(json[0]);
          if (json[0].length > 0) {
            setSelectedStation(json[0][0].value);
            // enable submit button
            setSubmitButtonDisabled(false);
            setSubmitButtonHidden(false);
          } else {
            setSelectedStation(undefined);
            // disable submit button
            setSubmitButtonDisabled(true);
            setSubmitButtonHidden(true);
          }
        } else {
          toast.error(t(json.description));
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  // Handler
  const handleSubmit = e => {
    e.preventDefault();
    loadData(APIBaseURL + '/reports/photovoltaicpowerstationdetails?id=' + selectedStation);
  };


  const refreshSVGData = () => {
    let isResponseOK = false;
    fetch(APIBaseURL + '/reports/pointrealtime', {
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
          json.forEach(currentPoint => {
            let textElement = document.getElementById('PT' + currentPoint['point_id']);
            if (textElement) {
              textElement.textContent = parseFloat(currentPoint['value']).toFixed(2);
            }
            let circleElement = document.getElementById('CIRCLE' + currentPoint['point_id']);
            if (circleElement) {
              if (currentPoint['value'] > 0) {
                circleElement.className.baseVal = 'flow';
              } else if (currentPoint['value'] < 0) {
                circleElement.className.baseVal = 'flow-reverse';
              } else {
                circleElement.className.baseVal = '';
              }
            }
          });
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  useInterval(() => {
    refreshSVGData();
  }, 1000 * 10);

  // Schedule
  const fetchScheduleDetails = () => {
    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/schedule'
    console.log('fetchScheduleDetails with url:' + url);
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
          setScheduleXaxisData(['00:00:00', '00:30:00', '01:00:00', '01:30:00', '02:00:00', '02:30:00', '03:00:00', '03:30:00', '04:00:00', '04:30:00', '05:00:00', '05:30:00', '06:00:00', '06:30:00',
          '07:00:00', '07:30:00', '08:00:00', '08:30:00', '09:00:00', '09:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00', '12:30:00', '13:00:00',  '13:30:00',
          '14:00:00', '14:30:00', '15:00:00', '15:30:00', '16:00:00', '16:30:00', '17:00:00', '17:30:00', '18:00:00', '18:30:00', '19:00:00', '19:30:00', '20:00:00', '20:30:00',
          '21:00:00', '21:30:00', '22:00:00', '22:30:00', '23:00:00', '23:30:00', '23:59:59']);
          setScheduleSeriesName('Power');
          setScheduleSeriesData(json['schedule']['series_data']);
          let schedule_mark_area_data = [];
          json['schedule']['schedule_list'].forEach((schedule_item, index) => {
            schedule_mark_area_data.push([{name: t(schedule_item['peak_type']), xAxis: schedule_item['start_time_of_day']}, {xAxis: schedule_item['end_time_of_day']}])
          });
          setScheduleMarkAreaData(schedule_mark_area_data);

        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }
  // PCS
  const fetchPCSDetails = () => {
    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/pcs'
    console.log('fetchPCSDetails with url:' + url);

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
          setPCSDetailsList(json);
        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }
  // BMS
  const fetchBMSDetails = () => {
    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/bms'
    console.log('fetchBMSDetails with url:' + url);
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
          setBMSDetailsList(json);
        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }
  // Meters
  const fetchMetersDetails = () => {

    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/meter'
    console.log('fetchMetersDetails with url:' + url);

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
          setMeterDetailsList(json);
        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }
  // HVAC
  const fetchHVACDetails = () => {
    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/hvac'
    console.log('fetchHVACDetails with url:' + url);
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
          setHVACDetailsList(json);
        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }
  // Fire Control
  const fetchFireControlDetails = () => {
    let url = APIBaseURL + '/reports/photovoltaicpowerstationdetails/' + selectedStation + '/firecontrol'
    console.log('fetchFireControlDetails with url:' + url);
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
          setFirecontrolDetailsList(json);
        } else {
          toast.error(t(json.description));

        }
      })
      .catch(err => {
        console.log(err);
      });
  }

  return (
    <Fragment>

      <Form onSubmit={handleSubmit}>
        <Row form>
          <Col xs={6} sm={3} hidden={spaceCascaderHidden}>
            <FormGroup className="form-group">
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
              <Form inline>
                <CustomInput
                  type="select"
                  id="stationSelect"
                  name="stationSelect"
                  bsSize="sm"
                  onChange={({ target }) => setSelectedStation(target.value)}
                >
                  {filteredStationList.map((station, index) => (
                    <option value={station.value} key={station.value}>
                      {station.label}
                    </option>
                  ))}
                </CustomInput>
              </Form>
            </FormGroup>
          </Col>
          <Col xs="auto">
            <FormGroup>
              <ButtonGroup id="submit">
                <Button size="sm" color="success" hidden={submitButtonHidden} disabled={submitButtonDisabled}>
                  {t('Submit')}
                </Button>
              </ButtonGroup>
            </FormGroup>
          </Col>
          <Col xs="auto">
              <FormGroup>
                <Spinner color="primary" hidden={spinnerHidden} />
              </FormGroup>
          </Col>
        </Row>
      </Form>
      <div  style={{ visibility: resultDataHidden ? 'visible' : 'hidden', display: resultDataHidden ? '': 'none' }}>
          <img className="img-fluid" src={blankPage} alt="" />
      </div>
      <div style={{ visibility: resultDataHidden ? 'hidden' : 'visible', display: resultDataHidden ? 'none': ''  }}>
        <Row noGutters>
          <Col lg="3" className="pr-lg-2">
            <Nav tabs>
              <NavItem className="cursor-pointer">
                <NavLink
                  className={classNames({ active: activeTabLeft === '1' })}
                  onClick={() => {
                    toggleTabLeft('1');
                  }}
                >
                  <h6>{t('Energy Indicator')}</h6>
                </NavLink>
              </NavItem>
              <NavItem className="cursor-pointer">
                <NavLink
                  className={classNames({ active: activeTabLeft === '2' })}
                  onClick={() => {
                    toggleTabLeft('2');
                  }}
                >
                  <h6>{t('Revenue Indicator')}</h6>
                </NavLink>
              </NavItem>
              {/* <NavItem className="cursor-pointer">
                <NavLink
                  className={classNames({ active: activeTabLeft === '3' })}
                  onClick={() => {
                    toggleTabLeft('3');
                  }}
                >
                  <h6>{t('Carbon Indicator')}</h6>
                </NavLink>
              </NavItem> */}
            </Nav>
            <TabContent activeTab={activeTabLeft}>
              <TabPane tabId="1">
                <Card className="mb-3 fs--1">
                  <Fragment>
                    <CardBody className="pt-0">
                      <Table borderless className="fs--1 mb-0">
                        <tbody>
                          <tr className="border-bottom">
                            <th className="pl-0">{t("Today's Charge")}</th>
                            <th className="pr-0 text-right">{todayChargeEnergyValue} kWh</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0">{t("Today's Discharge")}</th>
                            <th className="pr-0 text-right ">{todayDischargeEnergyValue} kWh</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Charge")}</th>
                            <th className="pr-0 text-right">{totalChargeEnergyValue} kWh</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Discharge")}</th>
                            <th className="pr-0 text-right">{totalDischargeEnergyValue} kWh</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Efficiency")}</th>
                            <th className="pr-0 text-right">{totalEfficiency}%</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Discharge Achievement Rate")}</th>
                            <th className="pr-0 text-right">{ (100 * todayDischargeEnergyValue / photovoltaicPowerStationRatedCapacity).toFixed(2)}%</th>
                          </tr>
                        </tbody>
                      </Table>
                    </CardBody>
                  </Fragment>
                </Card>
              </TabPane>
              <TabPane tabId="2">
                <Card className="mb-3 fs--1">
                  <Fragment>
                    <CardBody className="pt-0">
                      <Table borderless className="fs--1 mb-0">
                        <tbody>
                          <tr className="border-bottom">
                            <th className="pl-0">{t("Today's Cost")}</th>
                            <th className="pr-0 text-right">{todayChargeRevenueValue} 元</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0">{t("Today's Income")}</th>
                            <th className="pr-0 text-right ">{todayDischargeRevenueValue} 元</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Cost")}</th>
                            <th className="pr-0 text-right">{totalChargeRevenueValue} 元</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Income")}</th>
                            <th className="pr-0 text-right">{totalDischargeRevenueValue} 元</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Today's Revenue")}</th>
                            <th className="pr-0 text-right">{(todayDischargeRevenueValue - todayChargeRevenueValue).toFixed(2)} 元</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t("Total Revenue")}</th>
                            <th className="pr-0 text-right">{(totalDischargeRevenueValue - totalChargeRevenueValue).toFixed(2)} 元</th>
                          </tr>
                        </tbody>
                      </Table>
                    </CardBody>
                  </Fragment>
                </Card>
              </TabPane>
            </TabContent>
          </Col>
          <Col lg="6" className="pr-lg-2" key={uuidv4()}>
            <div dangerouslySetInnerHTML={photovoltaicPowerStationSVG} />
          </Col>
          <Col lg="3" className="pr-lg-2">
            <Nav tabs>
              <NavItem className="cursor-pointer">
                <NavLink
                  className={classNames({ active: activeTabRight === '1' })}
                  onClick={() => {
                    toggleTabRight('1');
                  }}
                >
                  <h6>{t('Device Status')}</h6>
                </NavLink>
              </NavItem>
              <NavItem className="cursor-pointer">
                <NavLink
                  className={classNames({ active: activeTabRight === '2' })}
                  onClick={() => {
                    toggleTabRight('2');
                  }}
                >
                  <h6>{t("Basic Information")}</h6>
                </NavLink>
              </NavItem>
            </Nav>
            <TabContent activeTab={activeTabRight}>
              <TabPane tabId="1">
                <DeviceStatusDetails
                  id={selectedStation}
                  gatewayStatus={gatewayStatus}
                  PCSStatus={PCSStatus}
                  BMSStatus={BMSStatus}
                  HVACStatus={HVACStatus}
                  gridMeterStatus={gridMeterStatus}
                  loadMeterStatus={loadMeterStatus}
                />
              </TabPane>
              <TabPane tabId="2">
                <Card className="mb-3 fs--1">
                  <Fragment>
                    <CardBody className="pt-0">
                      <Table borderless className="fs--1 mb-0">
                        <tbody>
                          <tr className="border-bottom">
                            <th className="pl-0">{t('Name')}</th>
                            <th className="pr-0 text-right">{photovoltaicPowerStationName}</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0">{t('Address')}</th>
                            <th className="pr-0 text-right ">{photovoltaicPowerStationAddress}</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t('Postal Code')}</th>
                            <th className="pr-0 text-right">{photovoltaicPowerStationPostalCode}</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t('Rated Capacity')} </th>
                            <th className="pr-0 text-right">{photovoltaicPowerStationRatedCapacity} kWh</th>
                          </tr>
                          <tr className="border-bottom">
                            <th className="pl-0 pb-0">{t('Rated Power')} </th>
                            <th className="pr-0 text-right">{photovoltaicPowerStationRatedPower} kW</th>
                          </tr>
                        </tbody>
                      </Table>
                    </CardBody>
                  </Fragment>
                </Card>
              </TabPane>
            </TabContent>
          </Col>
        </Row>

        <Nav tabs>
          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '1' })}
              onClick={() => {
                setActiveTabBottom('1');
              }}
            >
              <h6>{t('Operating Characteristic Curve')}</h6>
            </NavLink>
          </NavItem>
          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '2' })}
              onClick={() => {
                setActiveTabBottom('2');
                fetchScheduleDetails();
              }}
            >
              <h6>{t('Strategy Management')}</h6>
            </NavLink>
          </NavItem>
          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '3' })}
              onClick={() => {
                setActiveTabBottom('3');
              }}
            >
              <h6>{t('Fault Alarms')}</h6>
            </NavLink>
          </NavItem>

          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '4' })}
              onClick={() => {
                setActiveTabBottom('4');
                fetchPCSDetails()
              }}
            >
              <h6>PCS</h6>
            </NavLink>
          </NavItem>

          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '5' })}
              onClick={() => {
                setActiveTabBottom('5');
                fetchBMSDetails();
              }}
            >
              <h6>BMS</h6>
            </NavLink>
          </NavItem>

          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '6' })}
              onClick={() => {
                setActiveTabBottom('6');
                fetchMetersDetails();
              }}
            >
              <h6>{t('Meter')}</h6>
            </NavLink>
          </NavItem>

          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '7' })}
              onClick={() => {
                setActiveTabBottom('7');
                fetchHVACDetails();
              }}
            >
              <h6>{t('HVAC')}</h6>
            </NavLink>
          </NavItem>

          <NavItem className="cursor-pointer">
            <NavLink
              className={classNames({ active: activeTabBottom === '8' })}
              onClick={() => {
                setActiveTabBottom('8');
                fetchFireControlDetails();
              }}
            >
              <h6>{t('Fire Control')}</h6>
            </NavLink>
          </NavItem>
        </Nav>
        <TabContent activeTab={activeTabBottom}>
          <TabPane tabId="1">
            <MultipleLineChart
              reportingTitle=""
              baseTitle=""
              labels={parameterLineChartLabels}
              data={parameterLineChartData}
              options={parameterLineChartOptions}
            />
          </TabPane>
          <TabPane tabId="2">
            <ScheduleDetails
                xaxisData={scheduleXaxisData}
                seriesName={scheduleSeriesName}
                seriesData={scheduleSeriesData}
                markAreaData={scheduleMarkAreaData}
            />

          </TabPane>
          <TabPane tabId="3">
            <Card className="mb-3 fs--1">
              <CardBody className="bg-light">
                <Table striped className="border-bottom">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>主题</th>
                      <th>内容</th>
                      <th>创建时间</th>
                      <th>开始时间</th>
                      <th>结束时间</th>
                      <th>状态</th>
                      <th>更新时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="row">1</th>
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                    </tr>
                    <tr>
                      <th scope="row">2</th>
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                    </tr>
                    <tr>
                      <th scope="row">3</th>
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                    </tr>
                    <tr>
                      <th scope="row">4</th>
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                      <td />
                    </tr>
                  </tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPane>
          <TabPane tabId="4">
            {isIterableArray(PCSDetailsList) && PCSDetailsList.map(({ id, ...rest }) => <PCSDetails {...rest} key={id} />) }
          </TabPane>
          <TabPane tabId="5">
            {isIterableArray(BMSDetailsList) && BMSDetailsList.map(({ id, ...rest }) => <BMSDetails {...rest} key={id} />) }
          </TabPane>
          <TabPane tabId="6">
            {isIterableArray(meterDetailsList) && meterDetailsList.map(({ id, ...rest }) => <MeterDetails {...rest} key={id} />) }
          </TabPane>
          <TabPane tabId="7">
            {isIterableArray(HVACDetailsList) && HVACDetailsList.map(({ id, ...rest }) => <HVACDetails {...rest} key={id} />) }
          </TabPane>
          <TabPane tabId="8">
            {isIterableArray(firecontrolDetailsList) && firecontrolDetailsList.map(({ id, ...rest }) => <FirecontrolDetails {...rest} key={id} />) }
          </TabPane>
        </TabContent>
      </div>
    </Fragment>
  );
};

export default withTranslation()(withRedirect(PhotovoltaicPowerStationDetails));