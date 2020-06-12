sources = {
    "agents": {
        "query": """with maxTable as (
                        SELECT agent,
                            max(sequence) as maxSequence
                        FROM "agents"
                        WHERE __time > CURRENT_DATE
                        GROUP BY agent),
                        nextTable as (
                        SELECT a.agent Agents,
                            a.__time as ActivityTime,
                            a.sequence as Sequence,
                            b.sequence as NextSequence,
                            a.status as Status
                        FROM "agents" as a
                        LEFT JOIN "agents" as b
                            ON a.agent = b.agent
                            AND a.sequence = b.prevSequence
                        WHERE a.prevSequence > 0
                        AND a.__time > CURRENT_DATE),
                        resultTable as (
                        SELECT *,
                            (COALESCE(NextSequence, Sequence) - Sequence) / 1000 as Duration
                        FROM nextTable)

                        SELECT rt.Agents
                            ,rt.Status
                            ,sum(CASE WHEN rt.NextSequence is null THEN 1 ELSE 0 END) as IsLastAction
                            ,max(rt.ActivityTime) as ActivityTime
                            ,max(rt.Sequence) as Sequence
                            ,sum(rt.Duration) as SumDuration
                        FROM resultTable as rt
                        GROUP BY rt.Agents
                            ,rt.Status""",
        "dimensions": {
            "dim1": "Agents",
            "dim2": "Status"
        }
    },
    "calls" : {
        "query": """SELECT 'Total' as "Agent"
                        ,sum(duration) as "Sum of Duration"
                        ,sum(hold_time) as "Sum of Hold Time"
                        ,sum(ring_time) as "Sum of Ring Time"
                        ,sum(talk_time) as "Sum of Talk Time"
                        ,sum(acw) as "Sum of ACW Time"
                        ,count(*) as "Count of Calls"
                        ,count(DISTINCT campaign_id) as "Count of Unique Camp"
                    FROM "calls"
                    UNION ALL
                    SELECT *
                    FROM (
                    SELECT agent as "Agent"
                        ,sum(duration) as "Sum of Duration"
                        ,sum(hold_time) as "Sum of Hold Time"
                        ,sum(ring_time) as "Sum of Ring Time"
                        ,sum(talk_time) as "Sum of Talk Time"
                        ,sum(acw) as "Sum of ACW Time"
                        ,count(*) as "Count of Calls"
                        ,count(DISTINCT campaign_id) as "Count of Unique Camp"
                    FROM "calls"
                    GROUP BY agent
                    ORDER BY 6
                    ) as tbl"""
    }
}




# 'query':"""with maxTable as (
#             SELECT agent,
#                 max(sequence) as maxSequence
#             FROM "agents"
#             WHERE __time > CURRENT_DATE
#             GROUP BY agent),
#             nextTable as (
#             SELECT a.agent Agents,
#                 a.__time as ActivityTime,
#                 a.sequence as Sequence,
#                 b.sequence as NextSequence,
#                 a.status as Status
#             FROM "agents" as a
#             LEFT JOIN "agents" as b
#                 ON a.agent = b.agent
#                 AND a.sequence = b.prevSequence
#             WHERE a.prevSequence > 0
#             AND a.__time > CURRENT_DATE),
#             resultTable as (
#             SELECT *,
#                 (COALESCE(NextSequence, Sequence) - Sequence) / 1000 as Duration
#             FROM nextTable)

#             SELECT rt1.Agents,
#                 rt1.ActivityTime,
#                 rt1.Sequence,
#                 rt1.Status,
#                 sum(rt2.Duration) as SumDurationInSameStatus
#             FROM maxTable as mt
#             LEFT JOIN resultTable as rt1
#                 ON rt1.Sequence = mt.maxSequence
#             LEFT JOIN resultTable as rt2
#                 ON rt2.Agents = rt1.Agents
#                 AND rt2.Status = rt1.Status
#             GROUP BY rt1.Agents,
#                     rt1.ActivityTime,
#                     rt1.Sequence,
#                     rt1.Status"""