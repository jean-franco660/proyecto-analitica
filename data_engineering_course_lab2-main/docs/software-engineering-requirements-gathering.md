# Software Engineering Requirements Gathering Case Study

This document is a stakeholder interview scenario between a newly hired data
engineer and the software engineer responsible for the ecommerce sales platform.
It helps students practice gathering requirements from source system owners.

Source system owners are critical stakeholders because they control the systems
that generate and store the data used by downstream analytics, dashboards, and
machine learning pipelines.

## Scenario

The data scientist reported two common problems:

- Data is sometimes unavailable for longer than expected.
- Schema changes occasionally break processing scripts.

These are common issues in data engineering. To build reliable ingestion
pipelines, the data engineer needs to understand how the source system works,
what access patterns are safe, how outages are communicated, and how schema
changes are managed.

## Requirements Gathering Frame

When speaking with source system owners, the data engineer should focus on:

1. What existing system generates the data?
2. How is the data currently shared?
3. What problems do downstream users currently have?
4. What access patterns are safe for production?
5. How are outages and schema changes communicated?
6. What data contracts or APIs can provide stability?

## Stakeholder Interview

**Data engineer:** Hi, I'm Joe.

**Software engineer:** Hi. Good to meet you.

**Data engineer:** Nice to meet you too. I met with a marketing manager and a
data scientist. I'm looking forward to talking with you about how I can best set
up data ingestion from the sales platform.

**Software engineer:** Definitely. I think it is great that the company is
taking a more serious approach to data. I am looking forward to seeing how we can
work better together.

**Data engineer:** To start, I would like to learn more about what you have been
doing so far to provide data to other teams. Then we can take it from there.

**Software engineer:** To be honest, it feels like we are just getting started
exploring how to share data with other teams.

For example, the marketing team wants to analyze product sales data. We have been
providing data to the data scientists on a daily basis so they can provide
metrics to marketing.

But it sounds like marketing is looking for something closer to real-time
analytics.

**Data engineer:** I spoke with the data scientist and the product marketing
manager. More continuous access to data would definitely help with what they are
trying to do.

**Software engineer:** One problem is that we cannot give them direct access to
the production database. That would create risk for the sales platform.

That is what led us to the suboptimal solution of providing files for download
once per day.

**Data engineer:** That makes sense. Have you thought about other ways to
provide access to the data without creating risk for production?

**Software engineer:** Yes. I think one option would be to set up a read replica
of the production database. We would push a copy of everything stored in the
production database immediately after it is recorded.

Then we could set up an API so you, or anyone else, could query data in the read
replica without disturbing the production system.

**Data engineer:** That sounds like it could work well. The data scientist also
mentioned that sometimes they have to wait longer than expected for data. Would
the read replica setup help with that?

**Software engineer:** Yes and no.

Sometimes we miss regular data deliveries because we are running maintenance on
our systems and fail to export the regular files on time. With a continuously
updated read replica, that should not be a problem.

However, we do occasionally experience server or data center failures that cause
the platform or database to go down. We are working to add redundancies and
reduce exposure to system failures.

But if that happens, the data may be unavailable while the system is down. The
best thing we could do is send an automatic notification to downstream data
users to alert them of the outage.

**Data engineer:** That makes sense. If the systems generating and storing raw
data go down, the best downstream consumers can hope for is a notification.

I also heard that sometimes the database schema changes, and that causes
problems with processing scripts. Can you tell me more about your process for
schema changes?

**Software engineer:** Sure. We are constantly improving the sales platform, and
often that means adding new features for customers.

The user interaction data we record changes with each new feature, which
effectively changes the database schema.

We are also expanding into new regions and product lines. Sometimes we need to
add, remove, or combine elements of product and purchase records to keep up with
the changing things we sell and where we sell them.

**Data engineer:** How far in advance do you usually know when you will make a
schema change?

**Software engineer:** It varies, but we are usually careful because we do not
want to introduce breaking changes to our own systems. We typically know about a
week in advance before deploying new changes.

**Data engineer:** I am gathering requirements for the data pipelines we need to
support marketing. It would be helpful if I could stay in the loop about
upcoming database schema changes so I can anticipate them and modify pipelines
accordingly.

I can also build automatic checks into the ingestion process to verify whether
the data conforms to a particular schema. But it would be ideal to be notified as
soon as a schema change is being planned.

**Software engineer:** For sure. We can keep you in the loop. We do not want to
push changes that break downstream systems, so we can make sure you are notified
well in advance.

We can also think about making the read replica database more stable than the
production database.

For example, if you know exactly what data you need for customer activity or
purchase history, we can aim to provide that in a consistent way through the API
for the read replica.

If we cannot avoid changing something, we can at least give you plenty of
advance notice.

**Data engineer:** With advance notice of changes and some stability in the
database we ingest from, we should be in good shape.

Please let me know when the read replica database is set up, and I will start
building data pipelines for testing.

**Software engineer:** Will do.
