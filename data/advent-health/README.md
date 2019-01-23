# Advent Health

This data is entirely in XML, although the hospitals use different formats.

 - some use a workbook export
 - others have a single dataroot and then the hospital id.
 - it's not clear if these are inpatient or outpatient, so I'm assuming standard or average.

Data included are a price and description, there is no charge code, however
the descriptions are in all caps, which hints that they might be from some
ontology.

There are several files that were large to download, and thus were downloaded manually after programatic download left them empty. See the [issue here](https://github.com/vsoch/hospital-chargemaster/issues/5).


> How to read in the data

```python
df = pandas.read_csv('data-latest.tsv', sep='\t')
```

## Pricelist

The following is from [the pricelist site](https://www.adventhealth.com/pricelist) taken on January 23, 2019:

Helping Patients Make Informed Decisions
The Centers for Medicare & Medicaid Services (CMS) mandated hospital price transparency that went into effect January 1, 2019, whereby, Hospitals are required to make available a list of their current standard charges via the internet in a machine readable format and update this information at least annually, or more often as appropriate.

The federal government did not specify what format should be utilized. For purposes of the implementation of the Government Performance and Results Act (GPRA) Modernization Act, the Office of Management and Budget (OMB) defined "machine readable" as, “standard computer language that can be read automatically by a web browser or computer system.” Formats such as extensible markup language (XML), javascript object notation (JSON), and comma separated values (CSV) are deemed machine readable formats. Traditional word processing documents and portable document format (PDF) files are easily read by humans but typically are difficult for machines to interpret. Therefore, the files below represent the respective hospital’s pricelist in .xml format.

This format is a commonly utilized format that CMS utilizes for quality data submissions, and many other aspects of data sharing outlined in other CMS policy. However, provider organizations and patient advocates both agree that the realities of medical-industry pricing still make it difficult for consumers to comprehend this data. No patient ever pays the pricelist price. Insurance companies negotiate a specific discount for their customers. In addition, uninsured individuals have access to a variety of state and federal government programs and additional discounts that can be reviewed with a financial counselor prior to service.

Therefore, this file is not the best representation of the amount a patient or consumer will pay, because the final bill a patient receives is always discounted. Insurance companies negotiate discounts on the pricelist amounts by as much as 40% or more. In addition, patients’ have varying degrees of financial responsibility relative to how valuable their insurance coverage is. This means that patients will have higher or lower copays, co-insurances, and deductibles. The patient must pay an amount up to their deductible before the insurance begins paying benefits. These deductibles can be as low as five hundred dollars or as high as ten thousand dollars depending on how much coverage that individual purchased or their employer is providing on their behalf. In addition, after the deductible is paid by the patient, the patient will often owe 10-20% of the insurance’s negotiated amount up to a maximum individual or family amount. The patient’s coverage level as well as their insurance carrier’s negotiated amount may vary greatly, and therefore, the price each consumer pays is very personal.

For these reasons, AdventHealth aspires to give consumers meaningful information as they seek to restore their health. We believe consumers should be equipped with personalized and accurate estimates. We are making it easier for patients to make informed decisions about their health care by offering them personalized estimates for hospital procedures before their care. The estimates are based on their insurance coverage and the typical care experience for patients receiving similar services from the same physician. These personalized estimates are accessible in the “My Billing” section of this website.
