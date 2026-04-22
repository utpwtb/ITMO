package com.itmo.core.utils.models;

import java.util.ArrayList;
import java.util.List;

/**
 * 区间分析结果
 */
public class AnalysisResult {
    public boolean converges = true;
    public String divergeReason = "";
    public List<Range> validRanges = new ArrayList<>();
    public List<Range> cancelledRanges = new ArrayList<>();
}
