# Grand Tours Project for Erdos

## The general structure of database

Here we discuss the structure of the database, starting with the relational
table outlined below.

<!-- ![table structure](assets/readme_images/ss_2_12.png) -->

<img src="assets/readme_images/ss_2_12.png" width="650">

### The tour results dataset
The primary tables in our database are `tdf_results`, `giro_results` and
`vuelta_results`, which contain the historical data of the tours scraped from
[ProCyclingStats](https://www.procyclingstats.com), as an [example](https://www.procyclingstats.com/race/tour-de-france/2024/stage-20). These tables do not have primary keys (i.e., unique values) because their structure involves repeated entries for each rider across different stages and years, as shown below:

![Table structure example 1](assets/readme_images/ss_2_1.png)

<div style="display: flex; align-items: center;"> <img
  src="assets/readme_images/ss_2_2.png" alt="Description" style="width: 250px;
  margin-right: 20px;"> <p>Each row includes the rider's name, the time for a
    specific stage, and the stage properties, which repeat across different
    stages and years. Below the table, we have a summary of the columns using a single rider as an example. The columns in these tables are largely self-explanatory, with the possible exceptions of <code>profile_score</code> and <code>starlist_quality</code>.
    These terms have specific definitions, which can be found in the original
    source links. Unless Strava data is included, it is relatively
    straightforward to extract insights using SQL queries, provided the
    questions are well-defined. </p> </div>

### Strava datasets
<div style="display: flex; align-items: center;">
  <p>Working with Strava datasets requires a more intricate approach for both scraping and structuring. We start with the <code>strava_names</code> table, which contains riders' <code>names</code> and their unique <code>athlete_id</code>. While constructing this table, we assumed that the names in the <code>[tour]_results</code> table are unique (where [tour] = tdf, giro, or vuelta). This assumption is reasonable, as the dataset only includes results from 2010 onward, aligning with Strava's historical data coverage. </p> 
  <img src="assets/readme_images/ss_2_7.png" alt="Description" style="width: 250px; margin-right: 20px;">
</div>

The table `strava_names` is scraped by first taking the names of the riders from <code>[tour]_results</code> tables starting from 2010, then each name is searched through Strava search athlete tab. Once we have the result we simply choose the `athlete_id` number with the pro tag on in (see the image below).

<img src="assets/readme_images/ss_2_10.png" width="450">

After  forming the `strava_names` table we are now in a position to extract the data from riders profile. For that we first visit the riders main page which looks like the following.

![image](assets/readme_images/ss_2_11.png)

This page lists their activities weekly, so by using the date information from the <code>[tour]_results</code> tables  we can pinpoint each tour-week and scrape the `activity_id` generated throughout the event. Luckily, like the <code>athlete_id</code> each `activity_id` is unique. There is one thing we need to be careful though: although we scraped the activities during the event, by the nature of this scraping process we also extracted some extra activities. This is because, as you can imagine, some riders upload all of their rides including their ride to start-position or rides in their rest days and so on. Therefore, we need a way to clean those activities, which we will discuss after explaining the `segments_data` and `stats-data` tables.

The more data-intensive Strava tables are `segments_data` and `stats_data`. As the name suggests, `segments_data` is scraped from the segment information of a Strava ride. This table can become quite extensive, depending on the number of segments. It includes details such as time, speed, VAM ([velocità ascensionale media](https://en.wikipedia.org/wiki/VAM_(bicycling)) or "average ascent speed" in English), power, and heart rate—if the rider has chosen to upload these metrics.

![Table structure example 5](assets/readme_images/ss_2_5.png)

In the `segments_data` table, we chose to keep the `activity_id`, `athlete_id`, `date`, and `distance` fields explicit while bundling the `segments` data into a JSON blob. Since the `activity_id` serves as the primary key, it can efficiently distinguish between rides. A snapshot of the table can be seen below.

![Table structure example 3](assets/readme_images/ss_2_3.png)

The `stats_data` table contains general data scraped from Strava ride summaries. Since the type of data varies significantly between rides, it also makes sense to store this information as a JSON blob, similar to the `segments_data` table.

![Table structure example 6](assets/readme_images/ss_2_6.png)

An example of the structure of the `stats_data` table along with detailed column information for the `segments` and `stats` tables is shown below"

![Table structure example 4](assets/readme_images/ss_2_4.png)

Segments columns | Stats columns
:-------------------------:|:-------------------------:
![](assets/readme_images/ss_2_8.png) | ![](assets/readme_images/ss_2_9.png)

Finally, `strava_table` is basically merge of `segments_data` and `stats_data` tables and restricting them into race days so that there are no extra activities other than race data. We also choose the activities that are "close" to official distance. Below is the SQL query for the table construction using the data from `tdf_results`, `segments_data` and `stats_data`.

```sql
SELECT  t3.activity_id,
        t3.athlete_id,
        t3.tour_year,
	t3.strava_distance,
	t1.distance as official_distance,
        t3.DATE,
	t3.segment,
	t3.stat
        FROM(
SELECT
	t2.activity_id,
	t2.athlete_id,
	CAST(t2.`date` AS text) AS DATE,
	t2.tour_year,
	t2.distance as strava_distance,
	t2.segment,
	l.stat
FROM
	segments_data AS t2
LEFT JOIN stats_data AS l
	ON l.activity_id = t2.activity_id) as t3
INNER JOIN (SELECT
	DISTINCT(substr("--JanFebMarAprMayJunJulAugSepOctNovDec",
    strftime("%m", DATE) * 3, 3)||' '||CAST(strftime('%d', DATE) AS INTEGER)||' '||strftime('%Y', DATE)) AS tdf_date,
	stage, distance
FROM
	tdf_results
) AS t1
ON t1.tdf_date  = t3.DATE
WHERE (t1.distance-t1.distance * 0.2 ) < t3.strava_distance
AND t3.strava_distance < (t1.distance * 0.2 + t1.distance);

```
### Training datasets

## Training Methods
