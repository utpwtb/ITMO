package com.itmo.jmx;

import javax.management.*;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;
import java.lang.management.ManagementFactory;
import java.util.logging.Level;
import java.util.logging.Logger;

@WebListener
public class JMXConfig implements ServletContextListener {

    private static final Logger LOG = Logger.getLogger(JMXConfig.class.getName());

    private static final ObjectName POINTS_STATS_NAME = createObjectName("PointsStatistics");
    private static final ObjectName AREA_CALC_NAME   = createObjectName("AreaCalculator");

    private PointsStatistics pointsStatistics;
    private AreaCalculator areaCalculator;

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();

            pointsStatistics = new PointsStatistics();
            mbs.registerMBean(pointsStatistics, POINTS_STATS_NAME);
            LOG.info("Registered MBean: " + POINTS_STATS_NAME);

            areaCalculator = new AreaCalculator();
            mbs.registerMBean(areaCalculator, AREA_CALC_NAME);
            LOG.info("Registered MBean: " + AREA_CALC_NAME);

        } catch (Exception e) {
            LOG.log(Level.SEVERE, "Failed to register MBeans", e);
        }
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
            if (mbs.isRegistered(POINTS_STATS_NAME)) {
                mbs.unregisterMBean(POINTS_STATS_NAME);
                LOG.info("Unregistered MBean: " + POINTS_STATS_NAME);
            }
            if (mbs.isRegistered(AREA_CALC_NAME)) {
                mbs.unregisterMBean(AREA_CALC_NAME);
                LOG.info("Unregistered MBean: " + AREA_CALC_NAME);
            }
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "Failed to unregister MBeans", e);
        }
    }

    private static ObjectName createObjectName(String type) {
        try {
            return new ObjectName("com.itmo:type=" + type);
        } catch (MalformedObjectNameException e) {
            throw new RuntimeException(e);
        }
    }
}
